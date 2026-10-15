import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

export const metadata: Metadata = {
  title: "BC Co-op & Tech Job Tracker",
  description: "Daily-updated co-op and entry-level tech postings from British Columbia companies.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Sidebar />
        <main className="ml-[220px] min-h-screen">
          <div className="mx-auto max-w-[1100px] p-8">{children}</div>
        </main>
      </body>
    </html>
  );
}
