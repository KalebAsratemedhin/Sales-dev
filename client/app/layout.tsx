import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import { StoreProvider } from "@/components/providers/StoreProvider";
import { ConditionalShell } from "@/components/shared/ConditionalShell";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-outfit",
  display: "swap",
});

export const metadata: Metadata = {
  title: "SalesMind — Dashboard",
  description: "Autonomous SDR dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0"
          rel="stylesheet"
        />
      </head>
      <body className={`${outfit.variable} antialiased bg-background text-slate-100 font-sans`}>
        <StoreProvider>
          <ConditionalShell>{children}</ConditionalShell>
        </StoreProvider>
      </body>
    </html>
  );
}
