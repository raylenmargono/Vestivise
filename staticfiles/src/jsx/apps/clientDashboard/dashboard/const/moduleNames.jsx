/**
 * Created by raylenmargono on 12/15/16.
 */

const ReturnsModuleType = {
    RETURNS : "Returns",
    CONTRIBUTION_WITHDRAW : "Contributions and Withdraws",
    RETURNS_COMPARE : "Returns Comparison",
}

const FeesModuleType = {
    FEES : "Fees",
    COMPOUND_INTEREST : "Compound Interest",
}

const AssetModuleType = {
    HOLDING_TYPE : "Holding Types",
    STOCK_TYPE : "Stock Types",
    BOND_TYPE : "Bond Types",
}

const RiskModuleType = {
    RISK_PROFILE : "Risk/Returns Profile",
    RISK_AGE_PROFILE : "Risk/Age Profile",
    RISK_COMPARE : "Risks Comparison",
}

const ModuleType = Object.assign({},
    ReturnsModuleType,
    FeesModuleType,
    AssetModuleType,
    RiskModuleType
);

export {
    ReturnsModuleType,
    FeesModuleType,
    AssetModuleType,
    RiskModuleType,
    ModuleType
};