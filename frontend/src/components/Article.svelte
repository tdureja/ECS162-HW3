<script lang="ts">
  export let article: {
    headline: { main: string },
    snippet: string,
    pub_date: string,
    web_url: string,
    multimedia?: { url: string }[]
  };

  let imageUrl = article?.multimedia?.[0]?.url
    ? `https://www.nytimes.com/${article.multimedia[0].url}`
    : '';
</script>

<a class="article-link-wrapper" href={article.web_url} target="_blank">
  <div class="article-card article">
    {#if imageUrl}
      <div class="article-image">
        <img src={imageUrl} alt="Article Image" />
      </div>
    {/if}

    <div class="article-title">{article.headline.main}</div>
    <div class="article-date">{new Date(article.pub_date).toLocaleDateString()}</div>
    <div class="article-snippet">{article.snippet}</div>
  </div>
</a>
