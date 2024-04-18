import { Component } from '@angular/core';
import {GameHandlerService} from "../game-handler.service";
import {FormsModule} from "@angular/forms";

@Component({
  selector: 'app-game-page',
  standalone: true,
  imports: [
    FormsModule
  ],
  templateUrl: './game-page.component.html',
  styleUrl: './game-page.component.css'
})
export class GamePageComponent {
  gameText!: string;

  private typedGameText = "";
  currentWordText = "";
  private correctlyTypedAmount= 0;
  private wrongTypedAmount = 0;

  correctlyTypedText = "";
  wronglyTypedText = "";
  notTypedText = "";

  onCharacterTyped() {
    console.log("Hello")
    const currentWordStartIdx = this.typedGameText.length;
    this.correctlyTypedAmount = 0;
    this.wrongTypedAmount = 0;

    for(let i = 0; i < this.currentWordText.length; ++i) {
      if(this.wrongTypedAmount === 0 && this.currentWordText[i] === this.gameText[currentWordStartIdx + i]) {
        ++this.correctlyTypedAmount;

        if(this.gameText[currentWordStartIdx + i] === " ") {
          this.typedGameText += this.currentWordText;
          this.currentWordText = "";
        }
      } else {
        ++this.wrongTypedAmount;
      }
    }


    this.splitGameTextIntoParts();
  }

  private splitGameTextIntoParts() {
    const sumCorrectlyTypedAmount = this.correctlyTypedAmount + this.correctlyTypedText.length
    this.correctlyTypedText = "";
    this.wronglyTypedText = "";
    this.notTypedText = "";

    this.correctlyTypedText = this.gameText.slice(0, sumCorrectlyTypedAmount);
    this.wronglyTypedText = this.gameText.slice(sumCorrectlyTypedAmount, sumCorrectlyTypedAmount + this.wrongTypedAmount);
    if (this.wrongTypedAmount + sumCorrectlyTypedAmount < this.gameText.length) {
      this.notTypedText = this.gameText.slice(sumCorrectlyTypedAmount + this.wrongTypedAmount);
    }
  }

  ngOnInit() {
    this.gameText = this.gameHandlerService.getGameText();
    this.notTypedText = this.gameText;
  }



  constructor(private gameHandlerService: GameHandlerService) {
  }
}
