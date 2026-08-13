import type { MetadataRoute } from "next";
import { getAllMethods } from "@/lib/methods";

const BASE_URL = "https://startup-valuation.simonmak.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const methodPages: MetadataRoute.Sitemap = getAllMethods().map((m) => ({
    url: `${BASE_URL}/methods/${m.slug}`,
    lastModified: new Date(),
    changeFrequency: "monthly",
    priority: 0.8,
  }));

  return [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 1,
    },
    {
      url: `${BASE_URL}/sign-in`,
      lastModified: new Date(),
      changeFrequency: "yearly",
      priority: 0.3,
    },
    ...methodPages,
  ];
}
