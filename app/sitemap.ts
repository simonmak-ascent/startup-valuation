import type { MetadataRoute } from "next";
import { getAllMethods } from "@/lib/methods";

const BASE_URL = "https://startup-valuation.ascent-partners.com";

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
      url: `${BASE_URL}/zh`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/hk`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/why-open-source`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/skills`,
      lastModified: new Date(),
      changeFrequency: "monthly",
      priority: 0.6,
    },
    {
      url: `${BASE_URL}/public-companies`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.6,
    },
    {
      url: `${BASE_URL}/benchmarks`,
      lastModified: new Date(),
      changeFrequency: "weekly",
      priority: 0.6,
    },
    ...methodPages,
  ];
}
