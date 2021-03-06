var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
import { LitElement, css, html, property, customElement } from 'lit-element';
import { SharedStyles } from './shared-styles.js';
import { ButtonSharedStyles } from './button-shared-styles.js';
import { connect } from 'pwa-helpers/connect-mixin.js';
import { store } from '../store.js';
import { navigate } from '../actions/app.js';
// This element is *not* connected to the Redux store.
let ExerciseCard = class ExerciseCard extends connect(store)(LitElement) {
    // This element is *not* connected to the Redux store.
    constructor() {
        super(...arguments);
        this.category = "";
        this.subcategory = "";
        this.title = "";
        this.description = "";
        this.iconText = "";
    }
    static get styles() {
        return [
            SharedStyles,
            ButtonSharedStyles,
            css `
      
        :host {
          background-color: white;
          border-radius: 7px;
          height: 150px;
          width: 200px;
          box-shadow: 0px 1.5px 4px rgba(0, 0, 0, .4);
          text-align: center;
          margin: 10px;
        }

        .exercise-card-top-container {
          padding: 5px;
          width: 100%;
        }

        .exercise-card-top {
          display: flex;
          flex-direction: row;
          justify-content: space-between;
        }

        .exercise-card-top-left {

        }

        .exercise-icon {
          background-color: var(--app-primary-color);
          color: white;
          font-weight: 600;
          font-size: 10px;
          padding: 6.5px;
          text-align: center;
        }

        .exercise-card-top-center {
          text-transform: uppercase;
          font-weight: 600;
          font-size: 8px;
          color: gray;
          padding-top: 8px;
          padding-bottom: 8px
        }

        .exercise-card-top-right {
          width: 26.5px;
        }

        .exercise-card-center {
          border-top: 1px solid #efefef;
          border-bottom: 1px solid #efefef;
          height: 55px;
          display: flex;
          flex-direction: column;
          justify-content: center;
          padding: 10px;
        }

        .exercise-card-title {
          font-size: 14px;
          font-weight: 300;
          padding-bottom: 10px;
        }

        .exercise-card-description {
          font-size: 8px;
          font-weight: 300;
        }

        .exercise-card-bottom {
          width: 100%;
          font-size: 9px;
          font-weight: 400;
          color: var(--app-primary-color);
          display: flex;
          flex-direction: row
        }

        .exercise-card-bottom-left {
          width: 50%;
          padding-top: 10px;
          padding-bottom: 10px;
        }

        .exercise-card-bottom-right {
          border-left: 1px solid #efefef;
          width: 50%;
          padding-top: 10px;
          padding-bottom: 10px;
        }

      `
        ];
    }
    getFormattedSubcategory() {
        return this.subcategory.replace("-", " ");
    }
    beginSession() {
        store.dispatch(navigate("/guided-meditation"));
    }
    showDocumentation() {
        console.log("showing docs");
    }
    render() {
        return html `

    <div class="exercise-card-top-container">
      <div class="exercise-card-top">
        <div class="exercise-card-top-left">
          <div class="exercise-icon">${this.iconText}</div>
        </div>
        <div class="exercise-card-top-center">${this.getFormattedSubcategory()}</div>
        <div class="exercise-card-top-right"></div>
      </div>
    </div>
      <div class="exercise-card-center">
        <div class="exercise-card-title">${this.title}</div>
        <div class="exercise-card-description">${this.description}</div>
      </div>
      <div class="exercise-card-bottom">
        <div class="exercise-card-bottom-left" @click="${this.beginSession}">Begin session</div>
        <div class="exercise-card-bottom-right" @click="${this.showDocumentation}">Documentation</div>
      </div>

    `;
    }
};
__decorate([
    property({ type: String })
], ExerciseCard.prototype, "category", void 0);
__decorate([
    property({ type: String })
], ExerciseCard.prototype, "subcategory", void 0);
__decorate([
    property({ type: String })
], ExerciseCard.prototype, "title", void 0);
__decorate([
    property({ type: String })
], ExerciseCard.prototype, "description", void 0);
__decorate([
    property({ type: String })
], ExerciseCard.prototype, "iconText", void 0);
ExerciseCard = __decorate([
    customElement('exercise-card')
], ExerciseCard);
export { ExerciseCard };
