import { MetadataRoute } from 'next';
import { MOCK_DATA } from '../lib/mock-data';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const routes = [
    { url: 'https://indialens.in', lastModified: new Date(), changeFrequency: 'daily' as const, priority: 1 },
    { url: 'https://indialens.in/index', lastModified: new Date(), changeFrequency: 'daily' as const, priority: 0.9 },
    { url: 'https://indialens.in/methodology', lastModified: new Date(), changeFrequency: 'weekly' as const, priority: 0.8 },
    { url: 'https://indialens.in/analyze', lastModified: new Date(), changeFrequency: 'monthly' as const, priority: 0.8 },
  ];

  const collegeRoutes = MOCK_DATA.map((record) => ({
    url: `https://indialens.in/college/\${record.id}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.7,
  }));

  return [...routes, ...collegeRoutes];
}
