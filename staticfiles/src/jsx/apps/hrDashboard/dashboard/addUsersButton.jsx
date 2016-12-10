import React, {Component} from 'react';

class AddUsersButton extends Component{

    constructor(props){
        super(props);

        this.state = {
            selectedOption : false,
            isFileUpload : false,
            didDropFile: false
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
        $('#add-employee-modal').modal({
            complete: this.handleModalClose.bind(this)
        });
    }

    handleModalClose(){
        this.setState({
            selectedOption : false,
            isFileUpload : false,
            didDropFile : false
        });
    }

    getContainer(){
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
                selectedOption: true
            });
        }

        function uploadFileState(){
            this.setState({
                isFileUpload: true,
                selectedOption : true
            });
        }

        return (
            <div className="row">
                <div className="col m12">
                    <div className="row">
                        <div className="col m12 input-field">
                            <button onClick={uploadUserState.bind(this)} className="waves-effect waves-light btn max-width">Add User By Email</button>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col m12 input-field">
                            <button onClick={uploadFileState.bind(this)} className="waves-effect waves-light btn max-width">Import File</button>
                        </div>
                    </div>
                </div>
            </div>
        );
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
            <form>
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

    getSingleUploadContainer(){
        return (
            <form>
                <div className="row valign-wrapper input-row-text">
                    <div className="input-field col m10 valign center-block">
                        <input ref="username" placeholder="Email" id="email" name="email" type="text" />
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
            <div>
                <button data-target="add-employee-modal" id="add-user-button" className="waves-effect waves-light btn">
                    Add Users
                </button>
                <div id="add-employee-modal" className="modal">
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
            </div>

        );
    }

}


export default AddUsersButton;