import type { ParcelTypeId } from '../data/balanceConfig';
export class Parcel { constructor(public type: ParcelTypeId, public integrity = 100) {} damage(amount:number): void { this.integrity=Math.max(0,this.integrity-amount); } }
