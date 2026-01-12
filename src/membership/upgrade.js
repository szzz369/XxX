export const RULE_TYPES = {
  SPEND_TOTAL: 'spend_total',
  ORDER_COUNT: 'order_count',
  POINTS_TOTAL: 'points_total',
};

export function evaluateUpgrade({ currentLevelId, rules, stats }) {
  const eligibleLevels = rules
    .filter((rule) => isRuleSatisfied(rule, stats))
    .map((rule) => rule.memberLevelId);

  const highestEligibleLevel = eligibleLevels.sort((a, b) => b - a)[0];

  if (!highestEligibleLevel || highestEligibleLevel === currentLevelId) {
    return null;
  }

  return {
    fromLevelId: currentLevelId,
    toLevelId: highestEligibleLevel,
    matchedRuleIds: rules
      .filter((rule) => rule.memberLevelId === highestEligibleLevel)
      .map((rule) => rule.id),
  };
}

function isRuleSatisfied(rule, stats) {
  const threshold = Number(rule.thresholdValue);

  switch (rule.ruleType) {
    case RULE_TYPES.SPEND_TOTAL:
      return stats.spendTotal >= threshold;
    case RULE_TYPES.ORDER_COUNT:
      return stats.orderCount >= threshold;
    case RULE_TYPES.POINTS_TOTAL:
      return stats.pointsTotal >= threshold;
    default:
      return false;
  }
}
