import { ImageResponse } from 'next/og';
import { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const { searchParams } = new URL(request.url);
  const college = searchParams.get('college') || 'College';
  const degree = searchParams.get('degree') || 'Program';
  const score = searchParams.get('score') || 'N/A';
  
  return new ImageResponse(
    (
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'flex-start',
          width: '100%',
          height: '100%',
          backgroundColor: '#0A0A12',
          padding: '80px',
          fontFamily: 'sans-serif',
          color: '#F0F0F5',
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', maxWidth: '800px' }}>
          <span style={{ fontSize: '36px', color: '#8B8BA7', marginBottom: '10px' }}>
            {college}
          </span>
          <h1 style={{ fontSize: '72px', fontWeight: 'bold', color: '#F0F0F5', marginBottom: '40px', lineHeight: 1.1 }}>
            {degree}
          </h1>
          
          <div style={{ display: 'flex', alignItems: 'center' }}>
            <div style={{ 
              display: 'flex', 
              flexDirection: 'column',
              background: 'rgba(79, 110, 247, 0.1)', 
              border: '2px solid rgba(79, 110, 247, 0.4)',
              borderRadius: '20px',
              padding: '20px 40px',
              marginRight: '30px'
            }}>
              <span style={{ fontSize: '24px', color: '#8B8BA7', marginBottom: '10px', textTransform: 'uppercase' }}>Composite ROI</span>
              <span style={{ fontSize: '56px', color: '#4F6EF7', fontWeight: 'bold' }}>{score}/100</span>
            </div>
          </div>
        </div>
        
        <div style={{ 
          position: 'absolute', 
          bottom: '50px', 
          right: '80px',
          display: 'flex', 
        }}>
          <span style={{ fontSize: '36px', fontWeight: 'bold', color: '#F0F0F5' }}>
            India<span style={{ color: '#4F6EF7' }}>Lens</span>
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
