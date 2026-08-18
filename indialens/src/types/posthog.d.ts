declare module 'posthog-js' {
  const posthog: any;
  export default posthog;
}

declare module 'posthog-js/react' {
  import React from 'react';
  export const PostHogProvider: React.FC<{ client: any; children: React.ReactNode }>;
}
