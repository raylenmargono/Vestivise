import React from 'react';
import PremiumSubscriptionModal from './premiumSubscriptionModal.jsx';

class MenuFooter extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'MenuFooter';

        this.state ={
            currentModalInformation: ""
        };
    }

    displayInsightsModal(){
        this.setState({
            currentModalInformation : "insights"
        });
        $('#informationModal').openModal();
        $(".modal-content").scrollTop(0);

    }

    displayComparisonModal(){
        this.setState({
            currentModalInformation : "comparisons"
        });
        $('#informationModal').openModal();
        $(".modal-content").scrollTop(0);

    }

    render() {
        return (
            <div>
                <PremiumSubscriptionModal 
                    currentModalInformation={this.state.currentModalInformation}
                />
                <div id="footer" className="row">
                    <div id="bmenu-wrapper" className="col l12">
                       <ul className="bottommenu">
                       <li onClick={this.displayInsightsModal.bind(this)} className="bottommenu-left modal-trigger">Insights</li>
                       <li className="bottommenu-center">{this.props.module.toUpperCase()}</li>
                       <li onClick={this.displayComparisonModal.bind(this)} className="bottommenu-right modal-trigger">Comparisons</li>
                       </ul>
                   </div>
               </div>
           </div>
        );
    }
}

export default MenuFooter;