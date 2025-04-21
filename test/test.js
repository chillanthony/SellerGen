import { createClient } from 'pexels';

const client = createClient('77Z0EgePzT7djlGBVO6M6CzdGQYYkoyHIyF1Zt0QCUJi9RrQHPtmqCxm');
const query = 'Nature';

client.photos.search({ query, per_page: 1 }).then(photos => {
    console.log(photos); // 查看返回的结构

    const photo = photos.photos[0];
    console.log('照片地址:', photo.src.original);
});