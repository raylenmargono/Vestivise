/**
 * Created by raylenmargono on 12/15/16.
 */

const ReturnsModuleType = {
    RETURNS : "Returns",
    CONTRIBUTION_WITHDRAW : "Contributions and Withdrawals",
    RETURNS_COMPARE : "Returns Comparison",
};

const FeesModuleType = {
    FEES : "Fees",
    COMPOUND_INTEREST : "Bottom Line",
};

const AssetModuleType = {
    HOLDING_TYPE : "Holding Types",
    STOCK_TYPE : "Stock Types",
    BOND_TYPE : "Bond Types",
};

const RiskModuleType = {
    RISK_PROFILE : "Risk-Return Profile",
    RISK_AGE_PROFILE : "Risk-Age Profile",
};

const OtherModuleType = {
    PORT_HOLD : "Portfolio Holdings"
}

const ModuleType = Object.assign({},
    ReturnsModuleType,
    FeesModuleType,
    AssetModuleType,
    RiskModuleType,
    OtherModuleType
);

export {
    ReturnsModuleType,
    FeesModuleType,
    AssetModuleType,
    RiskModuleType,
    OtherModuleType,
    ModuleType
};