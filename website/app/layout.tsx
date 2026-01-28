import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HyperVolt - AI Energy Orchestrator",
  description: "Real-time energy management with predictive AI and carbon optimization",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
