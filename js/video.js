import { createClient } from 'pexels';

const args = process.argv.slice(2);
if (args.length === 0) {
  process.exit(1);
}

const query = args[0];
const client = createClient('77Z0EgePzT7djlGBVO6M6CzdGQYYkoyHIyF1Zt0QCUJi9RrQHPtmqCxm');

client.videos.search({ query, per_page: 5}).then(videos => {
    console.log(JSON.stringify(videos))
});