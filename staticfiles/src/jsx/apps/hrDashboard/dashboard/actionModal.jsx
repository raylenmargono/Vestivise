import React, {Component} from 'react';
import ReactDOM from 'react-dom';

class ActionModal extends Component{

    constructor(props){
        super(props);
        this.state = {
            selectedOption : false,
            isFileUpload : false,
            didDropFile: false,
            mode : "list" //list or detail
        }
    }

    componentDidUpdate(){
        if(this.state.isFileUpload){
            const drEvent = $('.dropify').dropify({
                messages: {
                    'default' : "",
                    "replace" : "",
                    'remove':  'Remove',
                    'error':   ''
                }
            });

            drEvent.on('dropify.afterClear', function(event, element){
                this.setState({
                   didDropFile: false
                });
            }.bind(this));

            drEvent.on('dropify.errors', function(event, element){
                this.setState({
                   didDropFile: false
                });
            }.bind(this));
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
            selectedOption : false,
            isFileUpload : false,
            didDropFile : false,
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

    getEditResponseContainer(){
        var response = this.props.editResponse;
        if("internalError" in response){
            return(
              <div>
                  <h5>Internal Error</h5>
                  <p>{response.errorMessage}</p>
              </div>
            );
        }
        var errors = response.errors.length;
        var success = response.success.length;
        return (
          <div>
              <div className="row">
                  <div className="col m2">
                      <h5 className="request-info">{success}</h5>
                  </div>
                  <div className="col m6">
                      <p>Requests sent</p>
                  </div>
              </div>
              <div className="row">
                  <div className="col m2">
                      <h5 className="request-info">{errors}</h5>
                  </div>
                  <div className="col m6">
                      <p>Requests failed</p>
                      <p className="grey-text small">Request failed to either employee exists or email is not valid</p>
                  </div>
              </div>
          </div>
        );
    }

    handleDeleteOrLinkDidFinish(){
        var success = this.props.editResponse.success ? "Success" : "Failure";
        return(
            <div className="row">
              <div className="col m12">
                  <h5 className="request-info">{success}</h5>
              </div>
          </div>
        );
    }

    getContainer(){
        if(Object.keys(this.props.editResponse).length !== 0){
            if(this.state.mode == "list"){
                return this.getEditResponseContainer();
            }
            return this.handleDeleteOrLinkDidFinish();
        }
        if(this.props.isLoading){
            return this.getLoadingContainer();
        }
        if(!this.state.selectedOption) {
            return this.getSelectOptionContainer();
        }
        if(this.state.isFileUpload){
            return this.getFileUploadContainer();
        }
        else{
            return this.getSingleUploadContainer();
        }
    }

    getSelectOptionContainer(){

        function uploadUserState(){
            this.setState({
                selectedOption: true,
                mode : "list"
            });
        }

        function uploadFileState(){
            this.setState({
                isFileUpload: true,
                selectedOption : true,
                mode : "list"
            });
        }

        function deleteUser(userOnEdit){
            this.setState({
                mode : "detail"
            });
            this.props.editAction.deleteUser(userOnEdit);
        }

        function resendUserConfirmationLink(userOnEdit){
            this.setState({
                mode : "detail"
            });
            this.props.editAction.resendUserConfirmationLink(userOnEdit);
        }


        var selectors = [
            {
                title : "Add User By Email",
                action : uploadUserState.bind(this)
            },
            {
                title : "Import File",
                action : uploadFileState.bind(this)
            }
        ];

        var userOnEdit = this.props.userOnEdit;

        if(userOnEdit){
            selectors = [
                {
                    title : "Delete User",
                    action : deleteUser.bind(this, userOnEdit)
                },
                {
                    title : "Resend invite",
                    action : resendUserConfirmationLink.bind(this, userOnEdit)
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

    uploadFile(e){
        e.preventDefault();
        var file = ReactDOM.findDOMNode(this.refs.fileUploadInput).files[0];
        this.props.editAction.createUserWithCSV(file);
    }

    getFileUploadContainer(){

        function didChangeFileInput(event){
            this.setState({
                didDropFile : event.target.value != ""
            });
        }

        function getButton(component){
            var cName = "waves-effect btn valign center-block max-width";
            var bTitle = "Submit";
            if(!component.state.didDropFile){
                cName += " disabled";
                bTitle = "Drop and drop file or click to submit";
            }
            return <button type="submit" className={cName}>{bTitle}</button>;
        }

        return (
            <form onSubmit={this.uploadFile.bind(this)}>
                <div className="row valign-wrapper input-row-text">
                    <div className="input-field col m12 valign center-block">
                        <input
                            name="employeeFile"
                            ref="fileUploadInput"
                            onChange={didChangeFileInput.bind(this)}
                            type="file"
                            className="dropify"
                            data-allowed-file-extensions="csv"
                        />
                    </div>
                </div>
                <div className="row valign-wrapper input-row">
                    <div className="input-field col m12 valign center-block">
                        {getButton(this)}
                    </div>
                </div>
            </form>
        );
    }

    oneEmployeeAdd(e){
        e.preventDefault();
        const email = this.refs.newUserEmailInput.value;
        this.props.editAction.createUserWithEmail(email);
    }

    getSingleUploadContainer(){
        return (
            <form onSubmit={this.oneEmployeeAdd.bind(this)}>
                <div className="row valign-wrapper input-row-text">
                    <div className="input-field col m10 valign center-block">
                        <input ref="newUserEmailInput" placeholder="Email" id="email" name="email" type="email" required/>
                        <p className="grey-text small">Login info and instructions will be sent to the users email.</p>
                    </div>
                </div>
                <div className="row valign-wrapper input-row">
                    <div className="input-field col m10 valign center-block">
                        <button type="submit" className="waves-effect btn valign center-block max-width">Submit</button>
                    </div>
                </div>
            </form>
        );
    }

    getTitle(){
        if(Object.keys(this.props.editResponse).length !== 0 || this.props.deleteOrLinkDidFinish) return "Results";
        if(this.props.isLoading) return "";
        if(!this.state.selectedOption) return "Select An Option";
        if(this.state.isFileUpload){
            return "Upload CSV File";
        }
        else{
            return "Enter Employee Email";
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