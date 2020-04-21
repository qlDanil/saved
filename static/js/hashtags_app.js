class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            hashtags: {
                'hashtag-1': 'orange',
                'hashtag-2': 'apple'
            }
        };
        this.deleteItem = this.deleteItem.bind(this);
        this.addItem = this.addItem.bind(this);
    }

    deleteItem(key) {
        delete this.state.hashtags[key];
        this.setState({
            hashtags: this.state.hashtags
        });
    }

    addItem(hashtag) {
        var timestamp = new Date().getTime();
        this.state.hashtags['hashtag-' + timestamp] = hashtag;
        this.setState({
            hashtags: this.state.hashtags
        });
    }

    render() {
        return React.createElement("div", {
            className: "component-wrapper"
        }, React.createElement(AddItemForm, {
            addItem: this.addItem,
            className: ""
        }), React.createElement(ItemList, {
            hashtags: this.state.hashtags,
            deleteItem: this.deleteItem,
            className: ""
        }));
    }

}

class ItemList extends React.Component {
    constructor(props) {
        super(props);
    }

    onDeleteClick(key, e) {
        e.preventDefault();
        this.props.deleteItem(key);
    }

    render() {
        return React.createElement("div", {
            className: "container"
        }, React.createElement("ul", {
            className: "list-inline text-center"
        }, Object.keys(this.props.hashtags).map(function (key) {
            return React.createElement("li", {
                className: "list-inline-item m-1 p-1 bg-white"
            }, "#", this.props.hashtags[key], " ", React.createElement("button", {
                onClick: e => this.onDeleteClick(key, e),
                type: "button",
                className: "close",
                "aria-label": "Close"
            }, React.createElement("span", {
                "aria-hidden": "true"
            }, "\xD7")), React.createElement("input", {
            type: "hidden",
            name: "hashtags[]",
            value: this.props.hashtags[key]
            }));
        }.bind(this))));
    }

}

class AddItemForm extends React.Component {
    constructor(props) {
        super(props);
        this.createItem = this.createItem.bind(this);
    }

    createItem(e) {
        e.preventDefault();
        var hashtag = this.refs.hashtagName.value;

        if (typeof hashtag === 'string' && hashtag.length > 0) {
            this.props.addItem(hashtag);
            this.refs.hashtagForm.reset();
        }
    }

    render() {
        return React.createElement("form", {
            className: "form-inline",
            ref: "hashtagForm",
            onSubmit: this.createItem
        }, React.createElement("div", {
            className: "form-group"
        }, React.createElement("label", {
                for: "hashtagItem"
            }, React.createElement("i", {
                className: "fas fa-hashtag",
            }, ""),
            React.createElement("input", {
                type: "text",
                id: "hashtagItem",
                placeholder: "Новый хештег",
                ref: "hashtagName",
                className: "form-control"
            }))), React.createElement("button", {
            type: "submit",
            className: "btn ml-1"
        }, "Добавить"));
    }

}

ReactDOM.render(React.createElement(App, null), document.getElementById('hashtags-app'));