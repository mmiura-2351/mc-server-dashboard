import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Minecraft Server Dashboard',
  description: 'Web-based management application for Minecraft servers',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
