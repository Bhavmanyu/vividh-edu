import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const title = searchParams.get('title') || 'IndiaLens — Degree ROI Index';
  const score = searchParams.get('score');
  const college = searchParams.get('college');

  return new ImageResponse(
    (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          width: '100%',
          height: '100%',
          backgroundColor: '#0A0A12',
          padding: '60px',
          fontFamily: 'sans-serif',
          color: '#F0F0F5',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', maxWidth: '900px' }}>
          {college && (
            <h2 style={{ fontSize: '32px', color: '#4F6EF7', marginBottom: '20px', textTransform: 'uppercase', letterSpacing: '2px' }}>
              {college}
            </h2>
          )}
          
          <h1 style={{ fontSize: '64px', fontWeight: 'bold', marginBottom: '40px', lineHeight: 1.2 }}>
            {title}
          </h1>

          {score && (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              background: 'rgba(34, 197, 94, 0.1)', 
              border: '2px solid rgba(34, 197, 94, 0.5)',
              borderRadius: '50px',
              padding: '20px 40px',
            }}>
              <span style={{ fontSize: '48px', color: '#22C55E', fontWeight: 'bold' }}>
                ROI Score: {score}/100
              </span>
            </div>
          )}

          {!score && (
            <div style={{ display: 'flex', alignItems: 'center', marginTop: '20px' }}>
              <span style={{ fontSize: '32px', color: '#8B8BA7', fontStyle: 'italic' }}>
                India's first quantitative education ROI platform
              </span>
            </div>
          )}
        </div>
        
        <div style={{ 
          position: 'absolute', 
          bottom: '40px', 
          display: 'flex', 
          alignItems: 'center',
          borderTop: '1px solid #1E1E2E',
          paddingTop: '20px',
          width: '80%',
          justifyContent: 'center'
        }}>
          <span style={{ fontSize: '28px', fontWeight: 'bold', color: '#4F6EF7' }}>
            IndiaLens.in
          </span>
        </div>
      </div>
    ),
    {
      width: 1200,
      height: 630,
    }
  );
}
