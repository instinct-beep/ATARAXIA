markdown
# Ataraxia — Privacy Policy

## Commitment

Ataraxia is built privacy-first. We do not store personally identifiable information (PII). All demographic inference is aggregate-only.

## What We Collect

| Data Type | What We Store |
|-----------|--------------|
| Post text | Stored (public content) |
| Post timestamp | Stored (ISO 8601 UTC) |
| Platform source | Stored |
| User identity | SHA-256 hash only (irreversible) |
| Hashtags, mentions | Stored (public metadata) |
| Post metrics | Stored (public) |

## What We Do NOT Collect

- Full names
- Email addresses
- Phone numbers
- Precise location
- Device identifiers
- IP addresses
- Private messages
- Profile images
- Bio text

## Demographic Inference

All demographic data is **aggregate only**. We never store:
- "User A is 28 years old"
- "User B lives in Mumbai"
- "User C speaks Marathi"

We only store counts:
- "35% of posts come from users inferred as 18–24"
- "28% of posts come from Maharashtra region"

## Compliance

- **DPDP Act 2023** (Digital Personal Data Protection Act, India)
- **GDPR principles** (data minimization, purpose limitation)
- **X Developer Agreement** — no redistribution of raw user data
- **Telegram Terms of Service**

## User Hashing

User IDs are hashed with SHA-256 before storage. This hash cannot be reversed. It is used only to:
- Count unique users
- Track interaction patterns
- Build network graphs

## Re-identification Risk

Aggregate demographic data with small sample sizes can theoretically allow re-identification. We mitigate this by:
- Minimum 10 posts per aggregate bucket
- No cross-referencing with external datasets
- No location finer than state level

## Data Retention

- Raw posts: 90 days
- Aggregates: 2 years
- Network graphs: 90 days

## Contact

For privacy concerns, contact the Ataraxia team.