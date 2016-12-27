import React, {Component} from 'react';
import {ModuleType} from 'jsx/apps/clientDashboard/dashboard/const/moduleNames.jsx';

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
                className="nav-clicker"
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
                                Your asset type split between stocks and bonds should move toward bonds as you age to stabilize
                                your account closer to retirement because bonds are typically considered lower risk
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
                            <li className="collection-item">Betting against the success of an asset to gain money as it goes down</li>
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
                        <li className="collection-item">A bond based around a commitment that another party with meet an arrangement</li>
                        <li className="collection-item">The original cash payment is returned when the terms are met</li>
                    </ul>
                    <h5>Corporate Bond</h5>
                    <ul className="collection">
                        <li className="collection-item">A bond issued by a corporation to raise money for a variety of reason</li>
                        <li className="collection-item">These are typically longer-term investments</li>
                    </ul>
                    <h5>Municipal Bond</h5>
                    <ul className="collection">
                        <li className="collection-item">A bond issued by a state, municipality, or county</li>
                        <li className="collection-item">These are often used to build highways, bridges, and schools</li>
                    </ul>
                    <h5>Securitized Bond</h5>
                    <ul className="collection">
                        <li className="collection-item">A security created by transforming groups of bonds through financial engineering</li>
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
                            Contribute as much as possible to your investment accounts as early as possible because this money when invested will grow with compound interest
                        </li>
                        <li className="collection-item">
                            Compound interest creates greater returns over time as the interest that was accrued previously also grows with interest
                        </li>
                    </ul>
                </div>
            </div>
        )
    }

    getReturnsComparisonDescription(){
        return (<div></div>);
    }

    getRiskReturnProfileDescription(){
        return (
            <div className="row">
                <div className="col m12">
                    <h5>Risk-Return</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            This gauge is based on a measure of how well your portfolio has performed historically against the risks you’ve taken
                        </li>
                    </ul>
                    <h5>Bad</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            Your returns don’t justify the level of risk in your portfolio
                        </li>
                    </ul>
                    <h5>Moderate</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            Your returns are acceptable given the level of risk in your portfolio
                        </li>
                    </ul>
                    <h5>Good</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            Your returns are fantastic given the level of risk in your portfolio
                        </li>
                    </ul>
                </div>
            </div>
        )
    }

    getRiskAgeProfileDescription(){
        return (
            <div className="row">
                <div className="col m12">
                    <h5>Risk-Age</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            This gauge measures your portfolio’s split between stocks and bonds
                        </li>
                        <li className="collection-item">
                            The best allocation is to make your bond percentage close to your age
                        </li>
                    </ul>
                    <h5>Bad</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            Your stock and bond split is bad for your age
                        </li>
                    </ul>
                    <h5>Moderate</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            Your stock and bond split could be moderately improved for your age
                        </li>
                    </ul>
                    <h5>Good</h5>
                    <ul className="collection">
                        <li className="collection-item">
                            Your stock and bond split is good for your age
                        </li>
                    </ul>
                </div>
            </div>
        )
    }

    getRiskComparisonDescription(){
        return (<div></div>);
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
                                As the price of goods increase, your ability to buy goods decreases all things the same
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
                result = this.getRiskReturnProfileDescription();
                break;
            case ModuleType.RISK_AGE_PROFILE:
                result = this.getRiskAgeProfileDescription();
                break;
            case ModuleType.RISK_COMPARE:
                result = this.getRiskComparisonDescription();
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
        switch(moduleName){
            case ModuleType.RETURNS:
                return (
                    <p className="grey-text"> Your returns are compared to your age base <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"1"} text={"benchmark fund"} /> <br/> ({moduleData["benchmarkName"]}).
                    </p>
                );
            case ModuleType.CONTRIBUTION_WITHDRAW:
                return (
                    <p className="grey-text">Over the past four years you have <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"2"} text={"contributed"} /> ${moduleData["total"]["contributions"]}, you have withdrawn ${moduleData["total"]["withdraw"]}, and you have netted a positive/negative ${moduleData["total"]["net"]}.
                    </p>
                );
            case ModuleType.RETURNS_COMPARE:
                return <p className="grey-text">Your age group for <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"3"} text={"comparisons"} /> with Vestivise users is {moduleData["ageGroup"]}.</p>;
            case ModuleType.FEES:
                return <p className="grey-text">Your fees are {moduleData["averagePlacement"]} than the average investor.</p>;
            case ModuleType.COMPOUND_INTEREST:
                return <p className="grey-text">
                            At your current rate of returns, contributions, and fees,
                            you will have ${moduleData["futureValues"][moduleData["futureValues"].length - 1]} at retirement age adjusted for <NavShower onClick={this.selectDescription.bind(this, moduleName, "inflation")} uID={"4"} text={"inflation"} />.
                            This does not account for <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"10"} text={"taxes"} />.
                        </p>;
            case ModuleType.HOLDING_TYPE:
                return <p className="grey-text">You have ${moduleData["totalInvested"]} invested across {moduleData["assetTypes"]} <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"5"} text={"asset types"} /></p>;
            case ModuleType.STOCK_TYPE:
                return <p className="grey-text">Your portfolio's stocks spread across {Object.keys(moduleData).length} <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"6"} text={"types"} />.</p>;
            case ModuleType.BOND_TYPE:
                return <p className="grey-text">Your portfolio's bonds spread across {Object.keys(moduleData).length} <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"7"} text={"types"} />.</p>;
            case ModuleType.RISK_PROFILE:
                return <p className="grey-text">Your <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"8"} text={"risk-return profile"} /> is characterized as {moduleData["riskLevel"]}.</p>;
            case ModuleType.RISK_AGE_PROFILE:
                return <p className="grey-text">Your <NavShower onClick={this.selectDescription.bind(this, moduleName)} uID={"9"} text={"risk-age profile"} /> is characterized as {moduleData["riskLevel"]}.</p>;
            case ModuleType.RISK_COMPARE:
                return <p className="grey-text">Your age group for comparisons with Vestivise users is {moduleData["ageGroup"]}.</p>;
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
                    <h5>{this.getTitle()}:</h5>
                    {this.getSubHeader()}
                </div>
            </div>
        );
    }

}


export default DescriptionFactory;