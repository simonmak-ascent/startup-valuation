import type { MethodConfig } from "../valuation/types";
import { scorecardConfig } from "./scorecard";
import { vcMethodConfig } from "./vc-method";
import { saasLtvConfig } from "./saas-ltv";

const methodConfigs: MethodConfig[] = [scorecardConfig, vcMethodConfig, saasLtvConfig];

export function getAllMethods(): MethodConfig[] {
  return methodConfigs;
}

export function getMethodBySlug(slug: string): MethodConfig | undefined {
  return methodConfigs.find((m) => m.slug === slug);
}
