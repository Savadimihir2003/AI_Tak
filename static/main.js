// main.js

document.addEventListener('DOMContentLoaded', function() {
    // Breaking news ticker fetch
    const ticker = document.getElementById('breaking-news');
    if (ticker) {
        fetch('/api/breaking-news')
            .then(res => {
                if (!res.ok) throw new Error('Network response was not ok');
                return res.json();
            })
            .then(data => {
                if (data.ticker) {
                    ticker.innerHTML = `<marquee>${data.ticker}</marquee>`;
                } else {
                    throw new Error('No ticker data');
                }
            })
            .catch(error => {
                console.error('Breaking news error:', error);
                ticker.innerHTML = '<span>Could not load breaking news.</span>';
            });
    }

    // Job search form handler
    const jobForm = document.getElementById('job-form');
    if (jobForm) {
        jobForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const domain = document.getElementById('domain').value.trim();
            const location = document.getElementById('location').value;
            const linksDiv = document.getElementById('job-links');
            linksDiv.innerHTML = '';
            if (domain && location) {
                const encodedDomain = encodeURIComponent(domain);
                const encodedLocation = encodeURIComponent(location);
                const portals = [
                    {
                        name: 'LinkedIn',
                        url: `https://www.linkedin.com/jobs/search/?keywords=${encodedDomain}&location=${encodedLocation}`
                    },
                    {
                        name: 'Naukri',
                        url: `https://www.naukri.com/${encodedDomain}-jobs-in-${encodedLocation}`
                    },
                    {
                        name: 'Google Jobs',
                        url: `https://www.google.com/search?q=${encodedDomain}+jobs+in+${encodedLocation}`
                    }
                ];
                portals.forEach(portal => {
                    const a = document.createElement('a');
                    a.href = portal.url;
                    a.target = '_blank';
                    a.rel = 'noopener noreferrer';
                    a.textContent = `Search on ${portal.name}`;
                    linksDiv.appendChild(a);
                });
            }
        });
    }
    // Infinite scroll for news
    let currentPage = window.initialPage || 1;
    let loading = false;
    function createNewsCard(item) {
        const card = document.createElement('div');
        card.className = 'news-card animated-card';
        if (item.image) {
            const img = document.createElement('img');
            img.src = item.image;
            img.alt = 'news image';
            img.className = 'news-image';
            img.style = 'width:100%;max-height:180px;object-fit:cover;border-radius:10px 10px 0 0;box-shadow:0 2px 8px #0ff1ce33;';
            card.appendChild(img);
        }
        const dateDiv = document.createElement('div');
        dateDiv.className = 'date';
        dateDiv.style = 'font-size:1.1em;font-weight:600;color:#0ff1ce;';
        dateDiv.textContent = item.date;
        card.appendChild(dateDiv);
        const tagsDiv = document.createElement('div');
        tagsDiv.className = 'tags';
        tagsDiv.style = 'font-size:0.95em;color:#fff;background:#0ff1ce55;padding:0.2em 0.7em;border-radius:6px;display:inline-block;margin-bottom:0.3em;';
        card.appendChild(tagsDiv);
        const classDiv = document.createElement('div');
        classDiv.className = 'class';
        classDiv.style = 'font-size:0.95em;color:#ff0;text-shadow:0 0 4px #0ff1ce;display:inline-block;margin-left:0.5em;';
        classDiv.textContent = item.class;
        card.appendChild(classDiv);
        const h3 = document.createElement('h3');
        h3.style = 'margin:0.5em 0 0.3em 0;';
        h3.textContent = item.title;
        card.appendChild(h3);
        const summaryDiv = document.createElement('div');
        summaryDiv.className = 'summary';
        summaryDiv.textContent = item.summary;
        card.appendChild(summaryDiv);
        const a = document.createElement('a');
        a.className = 'read-more';
        a.href = item.link;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = 'Read more';
        card.appendChild(a);
        return card;
    }

    function loadMoreNews() {
        if (loading) return;
        loading = true;
        fetch(`/api/news?page=${currentPage+1}`)
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data) && data.length > 0) {
                    data.forEach(item => {
                        newsCardsSection.appendChild(createNewsCard(item));
                    });
                    currentPage += 1;
                }
                loading = false;
            })
            .catch(() => { loading = false; });
    }

    window.addEventListener('scroll', function() {
        if ((window.innerHeight + window.scrollY) >= (document.body.offsetHeight - 300)) {
            loadMoreNews();
        }
    });

    // Expose initialPage from backend (set in Jinja2)
    if (window.initialPage === undefined && typeof initialPage !== 'undefined') {
        window.initialPage = initialPage;
    }

    // Infinite scroll
    const newsCardsSection = document.getElementById('news-cards');
    if (newsCardsSection) {
        let currentPage = window.initialPage || 1;
        let loading = false;
        let hasMore = true;

        function createNewsCard(item) {
            const card = document.createElement('div');
            card.className = 'news-card animated-card';
            
            if (item.image) {
                const img = document.createElement('img');
                img.src = item.image;
                img.alt = `News image for ${item.title}`;
                img.className = 'news-image';
                img.style.cssText = 'width:100%;max-height:180px;object-fit:cover;border-radius:10px 10px 0 0;box-shadow:0 2px 8px #0ff1ce33;';
                img.onerror = () => img.style.display = 'none';
                card.appendChild(img);
            }

            const dateDiv = document.createElement('div');
            dateDiv.className = 'date';
            dateDiv.style.cssText = 'font-size:1.1em;font-weight:600;color:#0ff1ce;';
            dateDiv.textContent = item.date;
            card.appendChild(dateDiv);

            if (item.tags) {
                const tagsDiv = document.createElement('div');
                tagsDiv.className = 'tags';
                tagsDiv.style.cssText = 'font-size:0.95em;color:#fff;background:#0ff1ce55;padding:0.2em 0.7em;border-radius:6px;display:inline-block;margin-bottom:0.3em;';
                tagsDiv.textContent = item.tags;
                card.appendChild(tagsDiv);
            }

            const classDiv = document.createElement('div');
            classDiv.className = 'class';
            classDiv.style.cssText = 'font-size:0.95em;color:#ff0;text-shadow:0 0 4px #0ff1ce;display:inline-block;margin-left:0.5em;';
            classDiv.textContent = item.class;
            card.appendChild(classDiv);

            const h3 = document.createElement('h3');
            h3.style.cssText = 'margin:0.5em 0 0.3em 0;';
            h3.textContent = item.title;
            card.appendChild(h3);

            const summaryDiv = document.createElement('div');
            summaryDiv.className = 'summary';
            summaryDiv.textContent = item.summary;
            card.appendChild(summaryDiv);

            const a = document.createElement('a');
            a.className = 'read-more';
            a.href = item.link;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.textContent = 'Read more';
            card.appendChild(a);

            return card;
        }

        function loadMoreNews() {
            if (loading || !hasMore) return;
            loading = true;

            fetch(`/api/news?page=${currentPage + 1}`)
                .then(res => {
                    if (!res.ok) throw new Error('Network response was not ok');
                    return res.json();
                })
                .then(data => {
                    if (Array.isArray(data) && data.length > 0) {
                        data.forEach(item => {
                            newsCardsSection.appendChild(createNewsCard(item));
                        });
                        currentPage += 1;
                        hasMore = data.length === 8; // If we got fewer items than expected, we've reached the end
                    } else {
                        hasMore = false;
                    }
                })
                .catch(error => {
                    console.error('Error loading more news:', error);
                    hasMore = false;
                })
                .finally(() => {
                    loading = false;
                });
        }

        // Infinite scroll handler
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) clearTimeout(scrollTimeout);
            scrollTimeout = setTimeout(() => {
                const scrolledToBottom = (window.innerHeight + window.scrollY) >= (document.body.offsetHeight - 800);
                if (scrolledToBottom) {
                    loadMoreNews();
                }
            }, 100);
        });
    }
});