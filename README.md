# Social-Media-Marketing

Does Social Media Engagement Lead to Purchases?

**Overview**

With the rise of social media in product marketing, what role does digital platforms play in purchasing decisions? This project aims to answer this question by using a synthetic dataset from Kaggle. 

**Methodology**

Using Python and SQL, this project explored the dataset to examine user behaviour at different stages of the advertising funnel, from ad exposure and engagement through to possible purchasing. Doing this allows us to identify patterns in user interactions and assess how engagement with digital advertising shapes purchasing outcomes. 

Data was sourced from [Kaggle](https://www.kaggle.com/datasets/alperenmyung/social-media-advertisement-performance). While this is dataset is synthetic, it is designed to imitate a realistic digital ad campaign ran by a business that follows a user's journey from their first exposure of the ad to a potential purchase. This dataset was generated using Python libraries, such as Faker and NumPy. 

Visualisations were created with Python and will be presented throughout this report. 

**Key Findings**

**1) Does digital engagement lead to purchases?**

While we may assume that digital advertising influences users' purchasing decisions, this is not the case within this synthetic dataset. Digital engagement does not appear to translate directly into purchases. Out of the 358 users, who engaged with the advertisement through likes, comments or shares, none made a purchase.

The funnel shows substantial drop-off at each stage: 100% Impression → 16.4% Click → 5.5% Like → 2.2% Comment → 1.1% Share → 0.56% Purchase 

The largest drop-off occurs between impression and click, with the proportion of users falling from 100% to 16.4%. This is an 83.6 percentage-point decrease, making the transition from simply seeing an advertisement to actively clicking it the most significant point of drop-off in the funnel. 

Therefore, exposure to digital advertising does not necessarily translate into active engagement or purchase behaviour. However, this is a synthetic dataset with a small sample size of 358 and these findings cannot be generalised to real-world consumer behaviour.

![Funnel Chart](https://github.com/ZaraTaza/Social-Media-Marketing/blob/main/visuals/funnel_chart.png)

**2) Comparing Platforms and Advertising Types**

Neither Facebook and Instagram had advantage in performance, with engagement being nearly identical in terms of clicks (16.3% vs 16.5%) and purchases (0.54% vs 0.57%). 

In terms of advertising types, stories had the highest purchase rate among ad formats at 0.59%, although the difference from other formats (video, image, carousel) was relatively small.

**3) Demographics**

Purchase rates were relatively similar across countries, with most falling between approximately 0.45% and 0.60% (a 0.15 percentage-point difference). Japan (0.71%) and Mexico (0.67%) had the highest purchase rates despite having broadly similar click rates to other markets. 

These differences could be due to factors such as pricing, localisation and target audience but this analysis does not investigate these factors.

![Country Demographics](https://github.com/ZaraTaza/Social-Media-Marketing/blob/main/visuals/country_chart.png)

**4) Campaign Budgeting and Efficiency**

Allocated budget per purchase varied substantially across campaigns, ranging from $118 to $6,512 (which is approximately a 55× difference). This suggests that larger allocated budgets do not necessarily correspond to greater budget efficiency. 

Please note that 2 of 50 campaigns (#16 and #43) had no associated ads and were excluded from the analysis.

![Campaign Efficiency](https://github.com/ZaraTaza/Social-Media-Marketing/blob/main/visuals/campaign_efficiency_chart.png)

**5) Weekly Trends**

Weekly clicks remained relatively stable across the period, generally ranging between approximately 2,950 and 3,150 per week. 

Purchases showed greater week-to-week variation, with a notable peak around week 24 and another increase towards week 30. However, there is no clear sustained upward or downward trend in either clicks or purchases over the period.

![Weekly Trends](https://github.com/ZaraTaza/Social-Media-Marketing/blob/main/visuals/weekly_trend_chart.png)

**Conclusion**

This analysis does not claim that social media is ineffective in digital marketing as it is based on a relatively small sample of synthetic data. 

However, there is no strong evidence of a relationship between social media engagement and purchasing behaviour. While users progressed through several stages of digital engagement, social interactions (such as likes, comments and shares) were not associated with higher purchase rates among users who clicked on an advertisement. Further analysis using real-world data would be needed to determine whether these patterns reflect actual consumer behaviour. Within this synthetic dataset, social media engagement appears to play a limited role in purchasing behaviour.
