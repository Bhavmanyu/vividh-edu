import { Metadata } from 'next';
import { MOCK_DATA } from '../../../lib/mock-data';

export async function generateMetadata({ params }: { params: { id: string } }): Promise<Metadata> {
  const record = MOCK_DATA.find(r => r.id === params.id);
  if (!record) return { title: 'Program Not Found' };
  
  return {
    title: `${record.college.name} - ${record.degree.name}`,
    description: `ROI score ${record.roi.compositeScore}/100. Median salary ₹${((record.salary?.year1?.p50 ?? 0) / 100000).toFixed(1)}L at graduation.`,
    openGraph: {
      images: [{ 
        url: `/api/og/college/${params.id}?college=${encodeURIComponent(record.college.name)}&degree=${encodeURIComponent(record.degree.name)}&score=${record.roi.compositeScore}`, 
        width: 1200, 
        height: 630 
      }],
    }
  };
}

export default function Layout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
