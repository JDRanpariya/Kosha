# Consumption Sources

- We want API first approch 
- If that fails we rely on data scraping
    - either scrapy or puppeteer
 
## TO DO
- [x] Implement Youtube
- [x] RSS
- [x] Spotify Podcast
- [x] Arxiv
 
### Python Design Patterns to follow
- https://refactoring.guru/design-patterns/python
- https://python-patterns.guide/
- https://youtu.be/vzTrLpxPF54?si=kDoBgMPa3GqE_Aqv&t=189
- https://www.youtube.com/watch?v=s_4ZrtQs8Do
- https://www.youtube.com/watch?v=5OzLrbk82zY
- https://www.youtube.com/watch?v=UPBOOIRrl40
- https://www.thedigitalcatbooks.com/pycabook-introduction/
- https://www.youtube.com/watch?v=wf-BqAjZb8M

### Responsibilities

1.  **Fetching content**
    -   RSS: poll new items
    -   YouTube: fetch uploads from subscribed channels
    -   Newsletters: parse IMAP or webhook events
    -   Podcasts: fetch RSS + transcripts

2.  **Parsing & Cleaning**
    -   Convert HTML / PDF / raw text → clean, readable text
    -   Extract metadata: title, author, date, URL, source

3.  **Deduplication & Normalization**
    -   Ensure same content from multiple sources isn't duplicated
    -   Normalize timestamps, categories, and media formats

4.  **Optional Enrichment**
    -   Generate transcripts for video/audio
    -   Summarization or embedding pre-processing (later stages)

### Consumption Sources
- [x] Move this to Ingetion Layer
- [ ] Personal Youtube Subscriptions
- [ ] Research Papers
  - [ ] arXiv Sanity Preserver to track ML related papers
  - [ ] Use PubMed Alerts, Google Scholar Alerts, and Semantic Scholar for neuroscience, biology, and anthropology.
  - [ ] Explore Services like Zotero, Paperpile, and Mendeley can help organize relevant papers.
  - [ ] AI based Filtering and clustering and abstract summarization.
    - [ ] AI-assisted Abstract Summarization and Relevance Scoring
    - [ ] Train an LLM (like GPT) on papers you find interesting to generate scores for relevance.
    - [ ] Use embeddings (like OpenAI's text-embedding-ada-002) to vectorize abstracts and compare them to abstracts you previously liked.
  - [ ] Tracking Research Trends Over Time???
  - [ ] Follow leading researchers on Google Scholar and ResearchGate to track influential publications?? 

### Youtube Subscriptions

### Research Papers
Keeping Track of Daily Paper Releases

You need a systematic approach that combines automation, AI, and manual review where needed.
1. Use APIs & Automation

    arXiv API & Semantic Scholar API
        Write a Python script that fetches all newly released AI, neuroscience, and math papers daily.
        Use NLP techniques to filter based on specific themes.

    Google Scholar & RSS Feeds
        Set up alerts for specific keywords (e.g., "neurosymbolic AI", "brain-inspired computing").
        Use Zotero + Notion to store & review abstracts later.

2. Summarizing & Categorizing

    LLM Summarization
        GPT-4 or Claude can summarize large paper batches.
        Use LangChain + OpenAI API to build a bot that categorizes papers.

    Cluster Papers by Topic
        Use TF-IDF, Word2Vec, or BERT embeddings to cluster similar abstracts.
        Visualize topic distributions using t-SNE or PCA in Python.

3. Prioritizing Important Research

    Monitor Citation Velocity
        Papers with rapidly increasing citations may indicate breakthroughs.
        Scite.ai and Litmaps help track citation networks.

    Look Beyond Hype
        Some papers are "hype-driven" but lack real impact.
        Analyze code availability and reproducibility studies.

1. Spotting Genuine Contributions

    Reproducibility:
        Check if the paper provides code (on GitHub, Hugging Face).
        Verify if independent researchers replicate findings.

    Novelty & Insights:
        Is it solving a problem that hasn’t been solved before?
        Does it introduce a fundamentally new perspective?

    Cross-disciplinary Impact:
        Truly valuable papers often connect AI with biology, neuroscience, cognitive science, or anthropology in novel ways.
        Monitor high-impact conferences (NeurIPS, ICML, CVPR, ICLR, AAAI, and cognitive science conferences).

2. Filtering Out Low-impact Research

    Identify "Paper Mills"
        Some conferences/journals prioritize quantity over quality.
        Avoid predatory journals with low peer-review standards.

    Analyze Citation Context
        If a paper gets cited but mostly in a negative or irrelevant way, it’s likely not a meaningful contribution.
        Use Scite.ai to check citation intent analysis.

### Podcasts
- [x] Spotify

### Conference Talks

### Events

### Curated blogs, newsletters and feeds
