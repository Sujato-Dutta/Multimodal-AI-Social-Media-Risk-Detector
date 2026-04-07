import "./globals.css";

export const metadata = {
  title: "Multimodal AI Risk Detector — Social Media Content Analysis",
  description:
    "AI-powered multimodal risk detection for social media content. Analyze images and captions for brand risk, offensive content, and misinformation using CLIP-based zero-shot classification.",
  keywords: [
    "AI",
    "risk detection",
    "social media",
    "content moderation",
    "CLIP",
    "multimodal",
  ],
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
