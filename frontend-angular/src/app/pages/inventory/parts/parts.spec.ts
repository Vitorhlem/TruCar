import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Parts } from './parts';

describe('Parts', () => {
  let component: Parts;
  let fixture: ComponentFixture<Parts>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Parts]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Parts);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
