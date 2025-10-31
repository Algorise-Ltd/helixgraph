# Mapping: Campaign.channel → Taxonomy

**Version:** v0.9  
**Last Updated:** 2025-10-12  

---

### Note  
This updated version introduces the `Media Platforms` layer under each channel taxonomy (e.g., Paid Search, Paid Social).  
All individual media platform names have been added without the term "Ads" for clarity and conciseness.  
The list will continue to be updated as new media platforms emerge.  
In this revision, channels are now explicitly classified under **Paid, Owned, and Earned Media** categories.  
Currently, this mapping references the **top 5 media platforms per channel type in Germany**, though the dominant platforms may vary by market.  

Additional updates aligned with **Marketing Channel Ontology v1.0** include:  
- *Influencer (Paid Collaboration)* renamed to **Branded Content / Creator Partnership** to match global terminology (Meta, TikTok, YouTube).  
- Added **Brand / Generic / Competitor** subtypes under *Paid Search* to reflect keyword intent classification.  
- Added **Prospecting / Retargeting** subtypes under *Paid Social* for consistency with Display and performance targeting structure.

---

# Paid Media  
Includes: SEM, SOCIAL, DISPLAY, AFFILIATE, EMAIL, PARTNERSHIP

## SEM (Paid Search)
Campaign.channel=Google → `SEM`  
Campaign.channel=Bing → `SEM`

### Subtypes
- Brand  
- Generic  
- Competitor

### Media Platforms
- Google  
- Bing  
- Ecosia  
- Yahoo!  
- DuckDuckGo

---

## SOCIAL (Paid Social)
Campaign.channel=Meta → `SOCIAL`  
Campaign.channel=TikTok → `SOCIAL`  
Campaign.channel=LinkedIn → `SOCIAL`  
Campaign.channel=Snapchat → `SOCIAL`  
Campaign.channel=X → `SOCIAL`

### Subtypes
- Prospecting  
- Retargeting  
*(auto-derive from `audience_targeting.retargeting`: true → Retargeting; false/missing → Prospecting)*

### Media Platforms
- Meta  
- TikTok  
- LinkedIn  
- X  
- Snapchat

---

## DISPLAY (Programmatic / Non-social Video & Display)
Campaign.channel=Google Display Network → `DISPLAY`  
Campaign.channel=The Trade Desk → `DISPLAY`  
Campaign.channel=Criteo → `DISPLAY`  
Campaign.channel=Adform → `DISPLAY`  
Campaign.channel=Taboola → `DISPLAY`

### Subtypes
- Prospecting  
- Retargeting  
*(auto-derive from `audience_targeting.retargeting`: true → Retargeting; false/missing → Prospecting)*

### Media Platforms
- Google Display Network  
- The Trade Desk  
- Criteo  
- Adform  
- Taboola

---

## AFFILIATE
Campaign.channel=Awin → `AFFILIATE`  
Campaign.channel=Rakuten → `AFFILIATE`  
Campaign.channel=Amazon Associates → `AFFILIATE`  
Campaign.channel=CJ Affiliate → `AFFILIATE`  
Campaign.channel=Tradedoubler → `AFFILIATE`

### Media Platforms
- Awin  
- Rakuten  
- Amazon Associates  
- CJ Affiliate  
- Tradedoubler

---

## EMAIL (Paid CRM)
Campaign.channel=Mailchimp → `EMAIL`  
Campaign.channel=Salesforce Marketing Cloud → `EMAIL`  
Campaign.channel=Klaviyo → `EMAIL`  
Campaign.channel=CleverReach → `EMAIL`  
Campaign.channel=Sendinblue → `EMAIL`

### Media Platforms
- Mailchimp  
- Salesforce Marketing Cloud  
- Klaviyo  
- CleverReach  
- Sendinblue

---

## PARTNERSHIP (Branded Content / Creator)
Campaign.channel=Instagram Paid Partnership → `PARTNERSHIP`  
Campaign.channel=TikTok Sponsored Content → `PARTNERSHIP`

### Media Platforms
- Instagram  
- TikTok  
- YouTube  
- Pinterest  
- Twitch

---

# Owned / Earned Media  
(Reference only; typically out of paid scope)

## ECOM (Owned)
Campaign.channel=Brand.com → `ECOM`  
Campaign.channel=Amazon → `ECOM`  
Campaign.channel=eBay → `ECOM`  
Campaign.channel=Zalando → `ECOM`  
Campaign.channel=Otto → `ECOM`

### Media Platforms
- Brand.com  
- Amazon  
- eBay  
- Zalando  
- Otto

---

## SEO / Organic (Earned)
Campaign.channel=Google Organic Search → `SEO`  
Campaign.channel=Bing Organic Search → `SEO`  
Campaign.channel=Blog Content → `BLOGS`

### Media Platforms
- Google  
- Bing  
- Blog Networks

---

## PR (Earned)
Campaign.channel=Press Release → `PR`  
Campaign.channel=Industry Magazines → `PR`

### Media Platforms
- Guardian  
- Telegraph  
- Handelsblatt  
- WirtschaftsWoche  
- Vogue Business

---

## Influencer (Organic Mentions)
Campaign.channel=Instagram Mentions → `EARNED_INFLUENCER`  
Campaign.channel=TikTok Mentions → `EARNED_INFLUENCER`  
Campaign.channel=YouTube Mentions → `EARNED_INFLUENCER`

### Media Platforms
- Instagram  
- TikTok  
- YouTube  
- Pinterest  
- Threads

