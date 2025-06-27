import type { Metadata } from 'next';
// eslint-disable-next-line @typescript-eslint/no-unused-vars
import { AuthProvider } from '@/contexts/AuthContext';
import './globals.css';
import { Toaster } from "@/components/ui/toaster";
import Header from '@/components/layout/header';
import Footer from '@/components/layout/footer';
import { Providers } from './providers'; // Import Providers
import { Inter, Space_Grotesk, Source_Code_Pro } from 'next/font/google';

// Configure the fonts
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter', // CSS variable for Inter
  display: 'swap',
});

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk', // CSS variable for Space Grotesk
  display: 'swap',
  weight: ['400', '500', '700'],
});

const sourceCodePro = Source_Code_Pro({
  subsets: ['latin'],
  variable: '--font-source-code-pro', // CSS variable for Source Code Pro
  display: 'swap',
  weight: ['400', '500'],
});

export const metadata: Metadata = {
  title: 'A2A Hire: Co-Agent Recruitment',
  description: 'AI agents collaborate via A2A to match companies and candidates perfectly, ensuring efficient, secure, and smart hiring.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${spaceGrotesk.variable} ${sourceCodePro.variable} dark`}>
      <head>
        {/* Remove existing Google Font <link> tags as next/font handles this */}
      </head>
      <body className="font-body antialiased flex flex-col min-h-screen">
        <Providers> {/* Wrap with Providers */}
          <Header />
          <main className="flex-grow container mx-auto px-4 py-8">
            {children}
          </main>
          <Footer />
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
