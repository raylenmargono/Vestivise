import React, {Component} from 'react';
import ReactDOM from 'react-dom';
import ListResponseView from './listResponseView.jsx';

class FileUploadView extends Component{

    constructor(props){
        super(props);
        this.state = {
            isFileUpload : false,
            didDropFile: false,
        }
    }

    componentDidMount(){
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

    uploadFile(e){
        e.preventDefault();
        var file = ReactDOM.findDOMNode(this.refs.fileUploadInput).files[0];
        this.props.editAction.createUserWithCSV(file);
    }

    didChangeFileInput(event){
            this.setState({
                didDropFile : event.target.value != ""
            });
        }

    getButton(){
        var cName = "waves-effect btn valign center-block max-width";
        var bTitle = "Submit";
        if(!this.state.didDropFile){
            cName += " disabled";
            bTitle = "Drag and drop file or click to submit";
        }
        return <button type="submit" className={cName}>{bTitle}</button>;
    }

    render(){
        if(!this.props.editResponse){
            return (
                <form onSubmit={this.uploadFile.bind(this)}>
                    <div className="row valign-wrapper input-row-text">
                        <div className="input-field col m12 valign center-block">
                            <input
                                name="employeeFile"
                                ref="fileUploadInput"
                                onChange={this.didChangeFileInput.bind(this)}
                                type="file"
                                className="dropify"
                                data-allowed-file-extensions="csv"
                            />
                        </div>
                    </div>
                    <div className="row valign-wrapper input-row">
                        <div className="input-field col m12 valign center-block">
                            {this.getButton()}
                        </div>
                    </div>
                </form>
            );
        }
        return <ListResponseView editResponse={this.props.editResponse}/>;
    }

}


export default FileUploadView;