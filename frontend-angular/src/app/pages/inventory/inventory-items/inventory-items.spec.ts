import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InventoryItems } from './inventory-items';

describe('InventoryItems', () => {
  let component: InventoryItems;
  let fixture: ComponentFixture<InventoryItems>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InventoryItems]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InventoryItems);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
