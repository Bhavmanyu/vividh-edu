import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { StatsBar } from "@/components/StatsBar";
import { Footer } from "@/components/Footer";
import { PostHogProvider } from "@/components/PostHogProvider";

export const metadata: Metadata = {
  title: {
    default: 'IndiaLens — Degree ROI Index',
    template: '%s | IndiaLens',
  },
  description: 'India\'s first quantitative education ROI platform. Compare degree × college combinations by salary trajectory, placement rates, and career risk.',
  keywords: ['India education', 'degree ROI', 'college rankings', 'salary after college', 'IIT placement', 'MBA ROI India'],
  openGraph: {
    type: 'website',
    locale: 'en_IN',
    url: 'https://indialens.in',
    siteName: 'IndiaLens',
    images: [{ url: '/api/og', width: 1200, height: 630 }],
  },
  twitter: {
    card: 'summary_large_image',
    site: '@indialens_in',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: { index: true, follow: true, 'max-image-preview': 'large' },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <PostHogProvider>
          <Navbar />
          <StatsBar />
          <main style={{ paddingTop: 84 }}>{children}</main>
          <Footer />
        </PostHogProvider>
      </body>
    </html>
  );
}

