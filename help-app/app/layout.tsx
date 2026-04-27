import "./globals.css";

export const metadata = {
  title: "ATP — Help",
  description: "Tài liệu hướng dẫn vận hành Autonomous Task Platform (ATP).",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <body>{children}</body>
    </html>
  );
}
