<script lang="ts">
  import { onMount } from 'svelte';
  import Header from './components/Header.svelte';
  import Article from './components/Article.svelte';

  interface ArticleType {
    _id: string;
    headline: { main: string };
    snippet: string;
    pub_date: string;
    web_url: string;
    multimedia: { url: string }[];
  }

  let articles: ArticleType[] = [];

  onMount(async () => {
    try {
      const res = await fetch('/api/articles');
      const data = await res.json();
      articles = data.articles;
      console.log('Fetched Articles:', articles);
    } catch (err) {
      console.error('Error fetching articles:', err);
    }
  });
</script>

<style global>
  @import './styles/style.css';
  @import './app.css';

  :root {
    font-family: system-ui, Avenir, Helvetica, Arial, sans-serif;
    line-height: 1.5;
  }
</style>

<main>
  <Header />
  <div class="content-grid">
    {#each articles as article (article._id)}
      <Article {article} />
    {/each}
  </div>
</main>