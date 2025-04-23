import { createClient } from 'pexels';

const client = createClient('77Z0EgePzT7djlGBVO6M6CzdGQYYkoyHIyF1Zt0QCUJi9RrQHPtmqCxm');
const query = parseInt(process.argv[2]);

client.videos.search({ query, per_page: 5 }).then(videos => {
    console.log(videos)
});