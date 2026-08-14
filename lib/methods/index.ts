import type { MethodConfig } from "../valuation/types";
import { capmConfig, startupCapmConfig } from "./capm";
import { peRatioConfig, psRatioConfig, evEbitdaConfig, evRevenueConfig } from "./comparables";
import { scorecardConfig, berkusConfig, vcMethodConfig, vcPreMoneyConfig, terminalValueConfig } from "./core";
import { gmvMultipleConfig, networkValueConfig } from "./marketplace";
import { poissonConfig } from "./probability";
import { saasLtvConfig, saasCacConfig, saasNrrConfig, saasMagicNumberConfig, saasRuleOf40Config, saasCacPaybackConfig, saasRevenueMultipleConfig } from "./saas";
import { dilutionConfig, commonDiscountConfig, opmConfig, ventureDebtConfig } from "./stakeholders";
import { presentValueConfig, annuityConfig } from "./tv";

const methodConfigs: MethodConfig[] = [
  capmConfig,
  startupCapmConfig,
  peRatioConfig,
  psRatioConfig,
  evEbitdaConfig,
  evRevenueConfig,
  scorecardConfig,
  berkusConfig,
  vcMethodConfig,
  vcPreMoneyConfig,
  terminalValueConfig,
  gmvMultipleConfig,
  networkValueConfig,
  poissonConfig,
  saasLtvConfig,
  saasCacConfig,
  saasNrrConfig,
  saasMagicNumberConfig,
  saasRuleOf40Config,
  saasCacPaybackConfig,
  saasRevenueMultipleConfig,
  dilutionConfig,
  commonDiscountConfig,
  opmConfig,
  ventureDebtConfig,
  presentValueConfig,
  annuityConfig,
];

export function getAllMethods(): MethodConfig[] {
  return methodConfigs;
}

export function getMethodBySlug(slug: string): MethodConfig | undefined {
  return methodConfigs.find((m) => m.slug === slug);
}
