export function calculateMembershipBenefits({
  subtotal,
  shippingFee,
  pointsEarned,
  memberLevel,
}) {
  const discountRate = memberLevel?.discountRate ?? 1;
  const pointsMultiplier = memberLevel?.pointsMultiplier ?? 1;
  const freeShippingThreshold = memberLevel?.freeShippingThreshold ?? null;

  const discountedSubtotal = roundCurrency(subtotal * discountRate);
  const shippingDiscount = calculateShippingDiscount({
    subtotal: discountedSubtotal,
    shippingFee,
    freeShippingThreshold,
  });
  const total = roundCurrency(discountedSubtotal + shippingFee - shippingDiscount);
  const finalPoints = Math.floor(pointsEarned * pointsMultiplier);

  return {
    discountedSubtotal,
    shippingDiscount,
    total,
    pointsMultiplier,
    finalPoints,
  };
}

function calculateShippingDiscount({ subtotal, shippingFee, freeShippingThreshold }) {
  if (freeShippingThreshold === null || freeShippingThreshold === undefined) {
    return 0;
  }

  if (subtotal >= freeShippingThreshold) {
    return shippingFee;
  }

  return 0;
}

function roundCurrency(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}
