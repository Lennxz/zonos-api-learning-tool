# Zonos API Learning Tool

An interactive learning tool for understanding and testing the Zonos API - designed for non-developers!

## Quick Start

```bash
cd ~/my-app
./start.sh
```

Or double-click `GraphQL Explorer.app`

This opens http://localhost:8000 in your browser.

## What This Tool Does

### For Learning (Non-Developers)
- **Visual journey map** showing how merchants use Zonos step-by-step
- **Plain English explanations** of each API call
- **Real-world analogies** to understand complex concepts
- **Pre-built queries** you can click and run

### For Testing (Technical)
- **GraphQL playground** to test actual API calls
- **Live responses** from Zonos API
- **Saved API credentials** (stored locally)

## The Merchant Journey (5 Steps)

1. **Customer Shops** - International buyer adds items to cart
2. **Calculate Landed Cost** - Zonos calculates duties, taxes, fees
3. **Customer Pays** - Total includes all import costs upfront
4. **Create Order** - Merchant registers order with Zonos
5. **Ship & Track** - Add tracking, Zonos handles customs payment

## Key APIs Explained

| API | What It Does | When Used |
|-----|--------------|-----------|
| `landedCostCalculateWorkflow` | Calculate duties/taxes/fees | At checkout |
| `orderCreate` | Record a sale in Zonos | After payment |
| `shipmentCreateWithTracking` | Add tracking number | After shipping |
| `orderCancel` | Cancel before shipping | Refunds/fraud |

## Webhooks vs API Calls

**This is a common point of confusion!**

- **API calls:** Merchant → Zonos (merchant asks for something)
- **Webhooks:** Zonos → Merchant (Zonos notifies about something)

Think of it like:
- API = You calling the pizza shop to order
- Webhook = Pizza shop calling YOU to say it's ready

## Files

- `index.html` - The learning tool UI
- `server.py` - Python proxy server (handles CORS)
- `start.sh` - Quick launcher script
- `GraphQL Explorer.app` - macOS app wrapper

## Getting Your API Key

1. Log into Zonos Dashboard
2. Go to Settings → Integrations
3. Click "Create GraphQL key"
4. Copy the `credential_live_xxx...` token

## Common Client Questions (From Your Emails)

Based on your onboarding experience, here are FAQs addressed in this tool:

1. **"How do I update order status?"** → Use `shipmentCreateWithTracking`
2. **"What's the difference between webhooks and API?"** → Direction! API = to Zonos, Webhooks = from Zonos
3. **"When do I get billed?"** → After you add tracking (order is fulfilled)
4. **"Can I cancel after shipping?"** → Complex - better to cancel before adding tracking

## Related Resources

- [Zonos API Docs](https://zonos.com/developer)
- [GraphQL Schema](https://zonos.com/developer/mutations)
- [Webhook Setup](https://zonos.com/docs/supply-chain/webhooks)

---

*This tool was built to help Lennon understand and demo Zonos APIs during client onboarding calls.*
