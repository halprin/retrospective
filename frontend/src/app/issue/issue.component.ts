import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'retro-issue',
  templateUrl: './issue.component.html',
  styleUrls: ['./issue.component.css']
})
export class IssueComponent implements OnInit {

  @Input() title = '';
  @Input() showDeleteButton = false;
  @Input() showDeleteSpinner = false;
  @Output() deleteButtonClicked = new EventEmitter();

  constructor() { }

  ngOnInit() {
  }

  delete() {
    this.deleteButtonClicked.emit();
  }
}
