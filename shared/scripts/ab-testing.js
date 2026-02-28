/**
 * Shopify Starter Templates — A/B Testing Framework
 * Lightweight client-side A/B testing with analytics integration
 */
(function () {
  'use strict';

  const SST_AB = {
    config: {
      storageKey: 'sst_ab_variants',
      cookieExpiry: 30, // days
      debug: false,
    },

    /** Get or assign a variant for an experiment */
    getVariant(experimentId, variants) {
      const stored = this._getStored();
      if (stored[experimentId]) return stored[experimentId];

      // Weighted random assignment
      const totalWeight = variants.reduce((sum, v) => sum + (v.weight || 1), 0);
      let random = Math.random() * totalWeight;
      let selected = variants[0].id;

      for (const variant of variants) {
        random -= variant.weight || 1;
        if (random <= 0) { selected = variant.id; break; }
      }

      stored[experimentId] = selected;
      this._setStored(stored);
      this._trackAssignment(experimentId, selected);
      return selected;
    },

    /** Apply variant to DOM elements */
    applyVariant(experimentId, variantId) {
      // Hide all variants, show the selected one
      document.querySelectorAll(`[data-ab-experiment="${experimentId}"]`).forEach(el => {
        el.style.display = el.dataset.abVariant === variantId ? '' : 'none';
      });
    },

    /** Track a conversion event */
    trackConversion(experimentId, eventName, value) {
      const variant = this._getStored()[experimentId];
      if (!variant) return;

      const event = {
        experiment: experimentId,
        variant: variant,
        event: eventName || 'conversion',
        value: value || 1,
        timestamp: Date.now(),
        url: window.location.href,
      };

      // Send to analytics
      this._sendEvent(event);

      if (this.config.debug) console.log('[AB]', event);
    },

    /** Initialize all experiments on the page */
    init() {
      const experiments = {};

      document.querySelectorAll('[data-ab-experiment]').forEach(el => {
        const expId = el.dataset.abExperiment;
        const varId = el.dataset.abVariant;
        const weight = parseFloat(el.dataset.abWeight) || 1;

        if (!experiments[expId]) experiments[expId] = [];
        if (!experiments[expId].find(v => v.id === varId)) {
          experiments[expId].push({ id: varId, weight });
        }
      });

      for (const [expId, variants] of Object.entries(experiments)) {
        const selected = this.getVariant(expId, variants);
        this.applyVariant(expId, selected);
      }

      // Track CTA clicks
      document.querySelectorAll('[data-ab-track]').forEach(el => {
        el.addEventListener('click', () => {
          const expId = el.closest('[data-ab-experiment]')?.dataset.abExperiment
            || el.dataset.abExperiment;
          if (expId) this.trackConversion(expId, 'click');
        });
      });
    },

    /* --- Private --- */

    _getStored() {
      try {
        return JSON.parse(localStorage.getItem(this.config.storageKey) || '{}');
      } catch { return {}; }
    },

    _setStored(data) {
      try { localStorage.setItem(this.config.storageKey, JSON.stringify(data)); } catch {}
    },

    _trackAssignment(experimentId, variantId) {
      this._sendEvent({
        experiment: experimentId,
        variant: variantId,
        event: 'assignment',
        timestamp: Date.now(),
      });
    },

    _sendEvent(event) {
      // Google Analytics 4
      if (typeof gtag === 'function') {
        gtag('event', 'ab_test', {
          experiment_id: event.experiment,
          variant_id: event.variant,
          event_action: event.event,
        });
      }
      // Meta Pixel
      if (typeof fbq === 'function') {
        fbq('trackCustom', 'ABTest', {
          experiment: event.experiment,
          variant: event.variant,
        });
      }
      // Beacon fallback
      if (window.__sst_analytics_endpoint) {
        navigator.sendBeacon(window.__sst_analytics_endpoint, JSON.stringify(event));
      }
    },
  };

  // Auto-init on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SST_AB.init());
  } else {
    SST_AB.init();
  }

  window.SST_AB = SST_AB;
})();
