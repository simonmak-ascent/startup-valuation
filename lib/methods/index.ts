import type { MethodConfig } from "../valuation/types";
import { scorecardConfig } from "./scorecard";
import { vcMethodConfig } from "./vc-method";
import { saasLtvConfig } from "./saas-ltv";
import { berkusConfig, vcPreMoneyConfig, terminalValueConfig } from "./core";
import {
  saasCacConfig,
  saasNrrConfig,
  saasMagicNumberConfig,
  saasRuleOf40Config,
  saasCacPaybackConfig,
  saasRevenueMultipleConfig,
} from "./saas";
import { peRatioConfig, psRatioConfig, evEbitdaConfig, evRevenueConfig } from "./comparables";
import { capmConfig, startupCapmConfig } from "./capm";
import { presentValueConfig, annuityConfig } from "./tv";
import { poissonConfig } from "./probability";
import { dilutionConfig, commonDiscountConfig, opmConfig, ventureDebtConfig } from "./stakeholders";
import { gmvMultipleConfig, networkValueConfig } from "./marketplace";

const methodConfigs: MethodConfig[] = [
  // Core
  scorecardConfig,
  berkusConfig,
  vcMethodConfig,
  vcPreMoneyConfig,
  terminalValueConfig,
  // SaaS
  saasLtvConfig,
  saasCacConfig,
  saasNrrConfig,
  saasMagicNumberConfig,
  saasRuleOf40Config,
  saasCacPaybackConfig,
  saasRevenueMultipleConfig,
  // Comparables
  peRatioConfig,
  psRatioConfig,
  evEbitdaConfig,
  evRevenueConfig,
  // CAPM / TV / Probability
  capmConfig,
  startupCapmConfig,
  presentValueConfig,
  annuityConfig,
  poissonConfig,
  // Stakeholders
  dilutionConfig,
  commonDiscountConfig,
  opmConfig,
  ventureDebtConfig,
  // Marketplace / Emerging
  gmvMultipleConfig,
  networkValueConfig,
];

export function getAllMethods(): MethodConfig[] {
  return methodConfigs;
}

export function getMethodBySlug(slug: string): MethodConfig | undefined {
  return methodConfigs.find((m) => m.slug === slug);
}
