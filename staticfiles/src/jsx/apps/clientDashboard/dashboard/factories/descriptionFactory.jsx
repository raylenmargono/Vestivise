import React, {Component} from 'react';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';
import {toUSDCurrency} from 'js/utils';

class NavShower extends Component{
    constructor(props){
        super(props);
    }

    componentDidMount(){
        $("#" + this.props.uID).sideNav({
            menuWidth: 400,
            edge: 'right',
            draggable: true
        });
    }


    selectedSpan(){
        $("#" + this.props.uID).sideNav('show');
        this.props.onClick();
    }

    render(){
        return (
            <span
                onClick={this.selectedSpan.bind(this)}
                className="nav-clicker hvr-underline-from-center"
                id={this.props.uID + "parent"}
            >
                <span
                    id={this.props.uID}
                    data-activates="slide-out"
                ></span>
                {this.props.text}
            </span>
        );
    }
}

class DescriptionFactory extends Component{

    constructor(props){
        super(props);
    }


    getHoldingTypeDescription(){
        return (
                <div className="row">
                    <div className="col m12">
                        <h5>Stocks</h5>
                        <ul className="collection">
                            <li className="collection-item">Portions of public traded companies that can be bought and sold </li>
                            <li className="collection-item">Can yield higher returns but also fall more quickly in value</li>
                        </ul>
                        <h5>Bonds</h5>
                        <ul className="collection">
                            <li className="collection-item">Investments where an entity lends money to another entity (e.g. government, company)</li>
                            <li className="collection-item">Guaranteed fixed rate of return on the initial investment that will be returned at a fixed date</li>
                            <li className="collection-item">
                                Many investors choose to move towards more bonds as they age because bonds are considered to be lower risk
                            </li>
                        </ul>
                        <h5>Cash</h5>
                        <ul className="collection">
                            <li className="collection-item">Mostly liquid investments used in exchange for other higher return investments</li>
                        </ul>
                        <h5>Other</h5>
                        <ul className="collection">
                            <li className="collection-item">
                                A catch-all category for special kinds of bonds and stocks, as well as various types of real estate funds and commodities
                            </li>
                        </ul>
                        <h5>Long Position</h5>
                        <ul className="collection">
                            <li className="collection-item">Purchasing an asset now in the hopes that it will be worth more later</li>
                        </ul>
                        <h5>Short Position</h5>
                        <ul className="collection">
                            <li className="collection-item">Betting against the success of an asset to gain money as it goes down in value</li>
                        </ul>
                    </div>
                </div>
        )
    }

    getStockTypeDescription(){
        return (
            <div className="row">
                <div className="col m12">
                    <h5>List of Stock Types</h5>
                    <ul className="collection">
                        <li className="collection-item">Communication</li>
                        <li className="collection-item">Consumer</li>
                        <li className="collection-item">Energy</li>
                        <li className="collection-item">Financial</li>
                        <li className="collection-item">Health Care</li>
                        <li className="collection-item">Industrials</li>
                        <li className="collection-item">Materials</li>
                        <li className="collection-item">Real Estate</li>
                        <li className="collection-item">Technology</li>
                        <li className="collection-item">Utilities</li>
                    </ul>
                </div>
            </div>
        )
    }

    getBondTypeDescription(){
        return (
            <div className="row">
                <div className="col m12">
                    <h5>Cash Bond</h5>
                    <ul className="collection">
                        <li className="collection-item">A bond based around a commitment that another party will meet an arrangement</li>
                        <li className="collection-item">The original cash payment is returned when the terms are met</li>
                    </ul>
                    <h5>Government Bonds</h5>
                    <ul className="collection">
                        <li className="collection-item">A bond issued by national governments</li>
                    </ul>
                    <h5>Derivative Bonds</h5>
                    <ul className="collection">
                        <li className="collection-item">A bond whose price is determined by the future value of another asset</li>
                    </ul>
                    <h5>Corporate Bond</h5>
                    <ul className="collection">
                        <li className="collection-item">A bond issued by a corporation to raise money for a variety of reasons</li>
                        <li className="collection-item">These are typically longer-term investments</li>
                    </ul>
                    <h5>Municipal Bond</h5>
                    <ul className="collection">
                        <li className="collection-item">A bond issued by a state, municipality, or county</li>
                        <li className="collection-item">These are often used to build highways, bridges, and schools</li>
                    </ul>
                    <h5>Securitized Bond</h5>
                    <ul className="collection">
                        <li className="collection-item">A bond based on the income from debt such as mortgages and other loans</li>
                    </ul>
                </div>
            </div>
        )
    }

    getReturnsDescription(){
        return (
            <div className="row">
                <div className="col m12">
                    <h5>Benchmark Fund</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            The investment portfolio for a person with similar retirement goals that tracks the overall market’s performance
                        </li>
                    </ul>
                </div>
            </div>
        )
    }

    getContributionWithdrawDescription(){
        return (
            <div className="row">
                <div className="col m12">
                    <h5>Why contribute to your portfolio?</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            Contributing as much as possible as early as possible can be beneficial because this investment then has the potential of growing with compound interest
                        </li>
                        <li className="collection-item">
                            Compound interest has the potential for creating greater returns over time as the interest that was accrued previously may continue to grow with interest
                        </li>
                    </ul>
                </div>
            </div>
        )
    }

    getReturnsComparisonDescription(){
        return (<div></div>);
    }

    getRiskReturnProfileDescription(param){
        if(param == "sp"){
            return (
                <div className="row">
                    <div className="col m12">
                        <h5>Sharpe Ratio</h5>
                        <ul className="collection">
                            <li className="collection-item">
                                The difference in return compared to the return of a risk free investment (such as a U.S. Treasury Bond) per unit of risk taken
                            </li>
                        </ul>
                        <ul className="collection">
                            <li className="collection-item">
                                You can think of this as a measure of how well your portfolio has performed historically against the risks you’ve taken
                            </li>
                        </ul>
                        <ul className="collection">
                            <li className="collection-item">
                                A higher sharpe ratio signifies a higher unit of return per unit of risk
                            </li>
                        </ul>
                    </div>
                </div>
            );
        }
        else{
            return(
                <div className="row">
                    <div className="col m12">
                        <h5>Risk-Return</h5>
                        <ul className="collection">
                            <li className="collection-item">
                                This gauge is based on a measure of how well your portfolio has performed historically against the risks you’ve taken
                            </li>
                        </ul>
                    </div>
                </div>
            );
        }
    }



    getRiskAgeProfileDescription(){
        return (
            <div className="row">
                <div className="col m12">
                    <h5>Risk-Age</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            This gauge measures your portfolio's split between stocks and bonds.
                        </li>
                    </ul>
                </div>
            </div>
        )
    }

    getFeeDescription(){
        return (
            <div className="row">
                <div className="col m12">
                    <h5>What’s so important about fees?</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            Consider an employee with 35 year until retirement and current balance of $25,000
                        </li>
                    </ul>
                    <ul className="collection">
                        <li className="collection-item">
                            Returns average 7% per year for the next 35 years
                        </li>
                    </ul>
                    <ul className="collection">
                        <li className="collection-item">
                            0.5% fees would produce a future balance of $227,000
                        </li>
                    </ul>
                    <ul className="collection">
                        <li className="collection-item">
                           1.5% fees would produce a future balance of $163,000 (28% less than 0.5% fees)
                        </li>
                    </ul>
                </div>
            </div>
        )
    }

    getBottomLineDescription(type){
        if(type == 'inflation'){
            return (
                <div className="row">
                    <div className="col m12">
                        <h5>Inflation</h5>
                        <ul className="collection">
                            <li className="collection-item">
                                As the price of goods increase, your ability to buy goods decreases
                            </li>
                        </ul>
                        <ul className="collection">
                            <li className="collection-item">
                                Inflation is assumed at 2% per year
                            </li>
                        </ul>
                        <ul className="collection">
                            <li className="collection-item">
                                A dollar today will not be worth a dollar in 30 years
                            </li>
                        </ul>
                    </div>
                </div>
            )
        }
        else{
            return (
                <div className="row">
                    <div className="col m12">
                        <h5>Tax Treatment</h5>
                        <ul className="collection">
                            <li className="collection-item">
                                Traditional accounts allow contributions of pre-tax dollars, and the money grows tax-sheltered
                                with qualified withdrawals eventually taxed as ordinary income
                            </li>
                        </ul>
                        <ul className="collection">
                            <li className="collection-item">
                                Roth accounts allow contributions of post-tax dollars,
                                and the money grows tax-sheltered with qualified withdrawals completely tax-free
                            </li>
                        </ul>
                    </div>
                </div>
            )
        }
    }

    
    selectDescription(moduleName, param){
        if(!moduleName) return;
        var result = null;
        switch(moduleName){
            case ModuleType.RETURNS:
                result = this.getReturnsDescription();
                break;
            case ModuleType.CONTRIBUTION_WITHDRAW:
                result = this.getContributionWithdrawDescription();
                break;
            case ModuleType.RETURNS_COMPARE:
                 result = this.getReturnsComparisonDescription();
                break;
            case ModuleType.FEES:
                result = this.getFeeDescription();
                break;
            case ModuleType.COMPOUND_INTEREST:
                result = this.getBottomLineDescription(param);
                break;
            case ModuleType.HOLDING_TYPE:
                result = this.getHoldingTypeDescription();
                break;
            case ModuleType.STOCK_TYPE:
                result = this.getStockTypeDescription();
                break;
            case ModuleType.BOND_TYPE:
                result = this.getBondTypeDescription();
                break;
            case ModuleType.RISK_PROFILE:
                result = this.getRiskReturnProfileDescription(param);
                break;
            case ModuleType.RISK_AGE_PROFILE:
                result = this.getRiskAgeProfileDescription();
                break;
            default:
                break;
        }
        this.props.appAction.renderNewNavElement(result);
    }

    getSubHeader(){
        const module = this.props.module;
        if(!module || !module.getData()) return;
        var moduleName = module.getName();
        var moduleData = module.getData();
        var moduleID = module.getID() + "id";
        switch(moduleName){
            case ModuleType.RETURNS:
                var n1 = <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={moduleID} text={"benchmark fund"} />;
                return (
                    <p > Your returns are compared to your age base {n1} <br/> ({moduleData["benchmarkName"]}).
                    </p>
                );
            case ModuleType.CONTRIBUTION_WITHDRAW:
                var c = toUSDCurrency(moduleData["total"]["contributions"]);
                var w = toUSDCurrency(moduleData["total"]["withdraw"]);
                var n = toUSDCurrency(moduleData["total"]["net"]);
                const nav = <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={moduleID} text={"contributed"} />;
                return (
                    <p>
                        Over the past four years you have {nav} {c}, you have withdrawn {w}, and you have netted a positive/negative {n}.
                    </p>
                );
            case ModuleType.RETURNS_COMPARE:
                return <p>Your age group for comparisons with Vestivise users is {moduleData["ageGroup"]}.</p>;
            case ModuleType.FEES:
                return <p>Your fees are {moduleData["averagePlacement"]} the industry average.</p>;
            case ModuleType.COMPOUND_INTEREST:
                var c = toUSDCurrency(moduleData["futureValuesMinusFees"][moduleData["futureValuesMinusFees"].length - 1]);
                var n1 = <NavShower onClick={this.selectDescription.bind(this, moduleName, "inflation")} uID={moduleID + "1"} text={"inflation"} />;
                var n2 = <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={moduleID + "2"} text={"taxes"} />;
                return <p>
                            At your current rate of returns, contributions, and fees,
                            you will have {c} at retirement age not adjusted for {n1}.
                            This does not account for {n2}.
                        </p>;
            case ModuleType.HOLDING_TYPE:
                var c = toUSDCurrency(moduleData["totalInvested"]);
                return <p>You have {c} invested across {moduleData["holdingTypes"]} <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={moduleID} text={"asset types"} /></p>;
            case ModuleType.STOCK_TYPE:
                return <p>Your portfolio's stocks spread across {moduleData["None"] ? 0 : Object.keys(moduleData).length} <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={moduleID} text={"types"} />.</p>;
            case ModuleType.BOND_TYPE:
                return <p>Your portfolio's bonds spread across {moduleData["None"] ? 0 : Object.keys(moduleData).length} <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={moduleID} text={"types"} />.</p>;
            case ModuleType.RISK_PROFILE:
                const a = <NavShower onClick={this.selectDescription.bind(this, moduleName, "sp")} uID={moduleID} text={"sharpe ratio"} />;
                const b = <NavShower onClick={this.selectDescription.bind(this, moduleName, "rr")} uID={moduleID + "2"} text={"risk-return profile"} />
                return <p>Your {a} is {moduleData["riskLevel"]}. Your age group for the {b} comparisons with Vestivise users is {moduleData["ageRange"]}.</p>;
            case ModuleType.RISK_AGE_PROFILE:
                const n = <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={moduleID} text={"risk-age profile"} />;
                return <p>Your age group for the {n} comparisons with Vestivise users is {moduleData["ageRange"]}.</p>;
            default:
                break;
        }
    }

    getTitle(){
        const module = this.props.module;
        if(!module) return;
        return module.getName();
    }

    render(){
        return(
            <div className="row">
                <div className="col m6">
                    <div className="description-container">
                        <h5>{this.getTitle()}</h5>
                        {this.getSubHeader()}
                    </div>
                </div>
            </div>
        );
    }

}


export default DescriptionFactory;