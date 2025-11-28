# Campaign Lifecycle States

**Version:** v0.9  
**Last Updated:** 2025-10-12  

---

### Note  
Defines the standardized campaign lifecycle states across all media channels and platforms.  
These states ensure consistent tracking, reporting, and synchronization with the `Campaign.status` field in `marketing_schema.json`.

| State | Description | Example Trigger |
|--------|--------------|-----------------|
| **PLANNED** | Campaign is configured but not yet activated. | Media plan approved, not live |
| **ACTIVE** | Campaign is currently running. | Ads serving on platform |
| **PAUSED** | Campaign temporarily stopped. | Budget hold, creative review |
| **COMPLETED** | Campaign has ended normally. | Scheduled end date reached |
| **CANCELLED** | Campaign was terminated early. | Client or system cancellation |
| **ARCHIVED** | Campaign is stored for reference after analysis. | Data retention phase |
