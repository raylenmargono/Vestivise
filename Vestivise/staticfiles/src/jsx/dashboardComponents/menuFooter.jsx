import React from 'react';

class MenuFooter extends React.Component {
    constructor(props) {
        super(props);
        this.displayName = 'MenuFooter';
    }
    render() {
        return (
        	<div id="footer" className="row">
			   	<div id="bmenu-wrapper" className="col l12">
				   <ul className="bottommenu">
				   <li className="bottommenu-left">Insights</li>
				   <li className="bottommenu-center">{this.props.module.toUpperCase()}</li>
				   <li className="bottommenu-right">Comparisons</li>
				   </ul>
			   </div>
		   </div>
        );
    }
}

export default MenuFooter;
