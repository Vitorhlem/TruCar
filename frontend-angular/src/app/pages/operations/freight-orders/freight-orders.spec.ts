import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FreightOrders } from './freight-orders';

describe('FreightOrders', () => {
  let component: FreightOrders;
  let fixture: ComponentFixture<FreightOrders>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FreightOrders]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FreightOrders);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
