import React, {Component} from 'react';
import DeleteUserView from './deleteUserView.jsx';
import FileUploadView from './fileUploadView.jsx';
import ResendConfView from './resendConfView.jsx';
import SingleUploadView from './singleUploadView.jsx';

const ViewStates = {
    fileUpload : 1,
    deleteUser : 2,
    resendConf : 3,
    singleUpload : 4
};

const GroupActions = {
    List : 1,
    Detail : 2
};

class ActionModal extends Component{

    constructor(props){
        super(props);
        this.state = {
            selectedOption : -1,
        }
    }

    componentDidMount(){
        $('#edit-modal').modal({
            complete: this.handleModalClose.bind(this)
        });
    }

    handleModalClose(){
        this.props.editAction.resetEditState();
        this.setState({
            selectedOption : -1,
        });
    }

    getLoadingContainer(){
        return(
            <div className="sk-wave">
                <div className="sk-rect green sk-rect1"></div>
                <div className="sk-rect green sk-rect2"></div>
                <div className="sk-rect green sk-rect3"></div>
                <div className="sk-rect green sk-rect4"></div>
                <div className="sk-rect green sk-rect5"></div>
            </div>
        );
    }

    getContainer(){
        if(this.props.isLoading){
            return this.getLoadingContainer();
        }
        switch(this.state.selectedOption){
            case ViewStates.fileUpload:
                return <FileUploadView editResponse={this.props.editResponse} editAction={this.props.editAction}/>;
            case ViewStates.singleUpload:
                return <SingleUploadView editResponse={this.props.editResponse} editAction={this.props.editAction}/>;
            case ViewStates.resendConf:
                return <ResendConfView modalActionData={this.props.modalActionData} editResponse={this.props.editResponse} editAction={this.props.editAction}/>;
            case ViewStates.deleteUser:
                return <DeleteUserView modalActionData={this.props.modalActionData} editResponse={this.props.editResponse} editAction={this.props.editAction}/>;
            default:
                return this.getSelectOptionContainer();
        }
    }

    getSelectOptionContainer(){

        function setViewState(state){
            this.setState({
                selectedOption : state,
            });
        }

         var selectors = [];

        if(this.props.modalActionData.action == GroupActions.Detail){
            selectors = [
                {
                    title : "Delete User",
                    action : setViewState.bind(this, ViewStates.deleteUser)
                },
                {
                    title : "Resend invite",
                    action : setViewState.bind(this, ViewStates.resendConf)
                }
            ];
        }
        else{
            selectors = [
                {
                    title : "Add User By Email",
                    action : setViewState.bind(this, ViewStates.singleUpload)
                },
                {
                    title : "Import File",
                    action : setViewState.bind(this, ViewStates.fileUpload)
                }
            ];
        }

        var rows = [];

        selectors.forEach(function(selector){
            rows.push(
                <div key={selector.title} className="row">
                    <div className="col m12 input-field">
                        <button onClick={selector.action} className="waves-effect waves-light btn max-width">{selector.title}</button>
                    </div>
                </div>
            );
        });

        return (
            <div className="row">
                <div className="col m12">
                    {rows}
                </div>
            </div>
        );
    }


    getTitle(){
        if(this.props.editResponse) return "Results";
        if(this.props.isLoading) return "";
        switch(this.state.selectedOption){
            case ViewStates.fileUpload:
                return "Upload CSV File";
            case ViewStates.singleUpload:
                return "Enter Employee Email";
            case ViewStates.resendConf:
                return "Retype Email to Send Confirmation";
            case ViewStates.deleteUser:
                return "Retype Email to Delete User";
            default:
                return "Select An Option";
        }
    }

    render(){

        return(
            <div id="edit-modal" className="modal">
                <div className="modal-content">
                    <h4>{this.getTitle()}</h4>
                    <div className="divider"></div>
                    <div className="valign-wrapper">
                        <div className="valign center-block max-width">
                            {this.getContainer()}
                        </div>
                    </div>
                </div>
            </div>

        );
    }
}


export default ActionModal;
export {GroupActions};