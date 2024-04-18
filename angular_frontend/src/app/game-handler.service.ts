import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class GameHandlerService {
  readonly gameText = "The only thing that you absolutely have to know, is the location of the library.";


  getGameText() {
    return this.gameText;
  }

  validateWord(word: string) {
    return this.gameText.split(" ").includes(word);
  }



  constructor() { }
}
