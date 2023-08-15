---
title: "Swift Macro: Revisited - Traps and Pitfalls"
category: Programming
tags: [Swift, Macro]
isPublished: false
---

In the previous post, we learned the strengths that uniquely define Swift
Macro. In the meanwhile, the examples in it work "so far so good".
However, can we be confident and bold, implementing any Swift macros we
want now?

No.

The features that bring Swift Macro advantages also introduce traps and
pitfalls which could lead to dead ends. Next, I would like to show you
several ones that I've found and how to overcome them.

## Traps and Pitfalls

### Potential Chaos in Control Flow

The `#unwrap` example in the previous post shows that Swift Macro
expansion could involve **control flow manipulation** and
**lexical scope sharing**:

Before expansion:

```swift
func foo(_ bar: Int?) {
  #unwrapped(bar) {
    print(bar)
  }
}
```

After expansion:

```swift
func foo(_ bar: Int?) {
  // #unwrapped expansion began
  guard let bar = bar else {
    return
  }
  print(bar)
  // #unwrapped expansion ended
}
```

Since the `return` statement in the macro expansion which manipulates the
control flow is an intentional behavior, this would not make us surprised.
But what if we put this macro in a loop? Here is an example:

Before expansion:

```swift
func foo(_ bar: Int?) {
  for _ in 0..<10 {
    #unwrap(bar) {
      print(bar)
    }
  }
}
```

After expansion:

```swift
func foo(_ bar: Int?) {
  for _ in 0..<10 {
    // #unwrapped expansion began
    guard let bar = bar else {
      return
    }
    print(bar)
    // #unwrapped expansion ended
  }
}
```

From the example shown above, we can learn that if we pass a non-optional
value to `foo`, the `bar` would only be printed once. This is because the
`return` statement involved by the macro expansion would break the outer
loop.

However, the `#unwrap` macro's name only shows its purpose is to unwrap
optional values but not to return from a function. This might cause the
programmer that uses this macro to think that returning is an
**unintentional behavior**.

### Name Conflicts in Freestanding Macro

However, **unintentional control flow manipulation** is not only one
potential pitfall in the expansion that I gave for the `#unwrap` macro.
One more pitfall here is that the `bar` variable was re-bound by the
`#unwarp` macro after the macro was expanded. Let's continue to examine
the expansion result of the previous example:

```swift
func foo(_ bar: Int?) {
  // #unwrapped expansion began
  guard let bar = bar else {
    return
  }
  print(bar)
  // #unwrapped expansion ended
}
```

This brought variable name shadowing where the `guard let bar: Int`
shadows the argument `_ bar: Int?`. In the case of `#unwrap`, the variable
name shadowing is trivial because it is an intentional behavior. However,
shadowing variables other than the `Optional`s could be considered as
unrecommended practice in real-world programming -- in fact, that would
not be compiled in Swift. As I concluded before, freestanding Swift macro
expansions involve lexical scope sharing with the applied site. This
enables potential variable shadowing in macro expansions. Here is a
contrived example, the variable name `updater` is shadowed due to the
macro expansion:

Before expansion:

```swift
func foo(_ bar: Int?) {
  let updater = Updater()
  #unwrap(fee, foe, fum) {
    let updater = Updater()
    print(bar)
    updater.update()
  }
  print(updater.description)
}
```

After expansion:

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return
  }
  // `updater` defined the second time
  let updater = Updater()
  print(bar)
  updater.update()
  // #unwrap expansion ended
  print(updater.description)
}
```

With a clean build in Xcode, you could find this example could not be
compiled:

TODO: A figure shows the compilation failure for the code above

### Name Conflicts in Attached Macro

Potential name conflicts not only be possible when freestanding macros
meet functions but also be possible when attached macros meet type
declarations. Let's recall the expansion result of the `@COW` macro
example in the previous post:

```swift
@COW
struct User {

  // @COW expansion began
  private class Storage {

    var name: String

    // other properties ...

  }

  private var _$storage: Storage

  private func makeStorageUniqueIfNeeded() {
    if !isKnownUniquelyReferenced(&_$storage) {
      _$storage = Storage(name: name, ...)
    }
  }

  init(name: String, ...) {
    self._storage = Storage(name: name, ...)
  }
  // @COW expansion ended

  // @COW expansion began
  @COWIncluded(storage: _$storage)
  // @COW expansion ended
  var name: String {
    // @COWIncluded expansion began
    get { return _$storage.name }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
    // @COWIncluded expansion ended
  }

}
```

You may have noticed that there is a member added in the expansion that is
named with a pattern that has a `_$` prefix.

```swift
  private var _$storage: Storage
```

This is a naming convention that I learned from Apple's implementation of
the macros in Swift Observation and SwiftData which keeps the
implementation details of an attached macro from the programmer's
unintentional access. However, this does not protect those members from
unintentional redeclaration or access brought by other macros -- there
could be other macros that are applied by the programmer which add members
with duplicate names or misuse members added by other macros.

For example, let's say there was a macro called `@DictionaryLike` which
makes the applied type behaves like a dictionary by adding a pair of
`subscript` getter and setter. Then we apply `@DictionaryLike` on the
`User` struct we used in the `@COW` macro example:

```swift
@DictionaryLike
struct User {

  // Other contents ...

}
```

The `@DictionaryLike` could be expanded as the following code:

```swift
@DictionaryLike
struct User {

  // Other contents ...

  // @DictionaryLike exapnsion began
  var _$storage: [String : Any] = [:]

  subscript(_ key: String) -> Any? {
    get { return _$storage[key] }
    set { _$storage[key] = newValue }
  }
  // @DictionaryLike exapnsion ended

}
```

Once we stack up `@COW` and `@DictionaryLike` together on the same type,
then there come to the situation that both `@COW` and `@DictionaryLike`
adds a member named `_$storage` to the applied type.

```swift
@COW
@DictionaryLike
struct User {

  // Other contents ...

  // Brought by @COW's expansion
  var _$storage: Storage

  // Brought by @DictionaryLike's expansion
  var _$storage: [String : Any] = [:]

}
```

This obviously would not get compiled in Swift because Swift does not
allow overloads on properties. We would get the “invalid redeclaration of
a variable” error again.

TODO: Compilation failure of the code above

### Name Conflicts for Unique Language Structures

The name collision is not the only pitfall of Swift Macro. Some language
structures in Swift are unique under the superstructure. This means when
multiple macros try to generate the same substructure in the same
superstructure, the code comes to be uncompilable.

We can contrive this by starting from the previous `@DictionaryLike`
example. Let's consider there is an attached accessor macro called
`@UseDictionaryStorage` which generates `get` and `set` accessor for the
attached property. The getter and setter forward access to the storage
which is brought by the expansion of `@DictionaryLike`.

Before macro expansion:

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  var info: [String : Any]?

}
```

After macro expansion:

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  var info: [String : Any]? {
    // @UseDictionaryStorage exapnsion began
    get {
      return _$storage["info"] as? [String : Any]?
    }
    set {
      _$storage["info"] = newValue
    }
    // @UseDictionaryStorage exapnsion ended
  }

}
```

However, that's oversimplified what happened. The real expansion result
with `@COW` macro is:

```swift
@COW
@DictionaryLike
struct User {
  
  @UseDictionaryStorage
  @COWIncluded
  var info: [String : Any]? {
    // @COWIncluded expansion began
    get {
      _$storage.info
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.info = newValue
    }
    // @COWIncluded expansion ended
    // @UseDictionaryStorage exapnsion began
    get {
      return _$storage["info"] as? [String : Any]?
    }
    set {
      _$storage["info"] = newValue
    }
    // @UseDictionaryStorage exapnsion ended
  }

}
```

We can observe that two `get` and `set` accessors are generated under the
`info` property. Since the Swift programming language grammar only allows
one `get`/`set` accessor in one property, this expansion would lead to
incorrect syntax in Swift and ultimately make the code not compile.

TODO: Previous code snippet does not compile

### Name Conflicts by Referring Declarations in Other Frameworks

Since we've learned several cases of potential name conflicts caused by
adding declarations, you might think that the list of name conflicts is
ended up.

But no. Name conflicts not only could be brought by declaring a variable,
a member of a type or an accessor, but also could be brought by referring
declarations in other frameworks. I would like to show you how we could
be cornered into this case by refactoring the `@COW` macro example.

The `@COW` macro example I've shown above is a naïve implementation. We
can extract the `makeStorageUniqueIfNeeded` function to a type called
`Box` that is bundled with the library containing the `@COW` macro. To
streamline the use of this type in macro expansions, we could make it a
property wrapper.

```swift
@propertyWrapper
public struct Box<Contents> {
  
  private class Heap {
    
    var contents: Contents
    
    init(contents: Contents) { self.contents = contents }
    
  }
  
  private var heap: Heap
  
  public init(wrappedValue: Contents) {
    heap = Heap(contents: wrappedValue)
  }
  
  public var wrappedValue: Contents {
    get { heap.contents }
    set {
      makeUniqueHeapIfNeeded()
      heap.contents = newValue
    }
  }
  
  private mutating func makeUniqueHeapIfNeeded() {
    guard !isKnownUniquelyReferenced(&heap) else { return }
    heap = Heap(contents: heap.contents)
  }
  
}
```

Then we can attach `@Box` in the `_$storage` property brought by the macro
expansion such that we can eliminate generating the
`makeStorageUniqueIfNeeded` function in place. This reduces redundant
generated code and increased the speed of compilation.

```swift
@COW
struct User {

  // @COW expansion began
  private struct Storage {

    var name: String

    // other properties ...

  }

  @Box
  private var _$storage: Storage

  init(name: String, ...) {
    self._$storage = Storage(name: name, ...)
  }
  // @COW expansion ended

  // @COW expansion began
  @COWIncluded(storage: _$storage)
  // @COW expansion ended
  var name: String {
    // @COWIncluded expansion began
    get { return _$storage.name }
    set { _$storage.name = newValue }
    // @COWIncluded expansion ended
  }

}
```

However, the type name `Box` may be ambiguous -- there could be other
frameworks that also have a type called `Box`. When ambiguity is
encountered, the code would come to be uncompilable.

TODO: Figure about the ambiguity of resolving `Box`

### Semantics Conflicts

In the `@DictionaryLike` macro example, we've learned that accessor macro
would affect each other. However, this is not the only potential pitfall
brought by accessor macros: some language features could also be
interfered with by attached macros. Look at the following example: a
property wrapper makes the code not compiled by being attached to a stored
property in a struct applied `@COW` macro.

Before the expansion:

```swift
@propertyWrapper
struct Capitalized {
  
  var wrappedValue: String {
    didSet {
      wrappedValue = wrappedValue.capitalized
    }
  }
  
}

@COW
struct User {
  
  @Capitalized
  var name: String = ""
  
}
```

After the expansion:

```swift
@COW
struct User {
  
  @COWIncluded
  @Capitalized
  var name: String = "" {
    get {
      return _$storage.name
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
  }

  // ...

}
```

We got this expansion result because the property wrapper "expansion"
happens later than the macro expansion. With this result, the
`@Capitalized` property wrapper is still attached to the `name` variable
but the variable is changed from a stored property into a computed
property due to the macro expansion. Eventually, we would get an error
diagnosed by the compiler:

> Property wrapper cannot be applied to a computed property

TODO: Replace with Xcode screenshot

This does not only happen along with property wrappers, the `lazy` keyword
could also lead to the same dead end.

```swift
@COW
class User {
  
  lazy var name: String = { "Jane Doe" }()
  
}
```

```swift
@COW
class User {
  
  @COWIncluded
  lazy var name: String = { "Jane Doe" }() {
    get {
      return _$storage.name
    }
    set {
      makeStorageUniqueIfNeeded()
      _$storage.name = newValue
    }
  }

  // ...

}
```

TODO: Replace with Xcode screenshot

With these examples, we can learn that the expansion of a Swift macro
could change the semantics of the source code. This could lead to a
semantics conflict and ultimately make the expansion result not compile.

## Solutions

Till now, we've had a list of typical traps and pitfalls that one could
step into while implementing Swift macros. At a glance, this list might
seem overwhelming to you. However, I concluded a simple way to get rid of
them: progressive control in macro expansion -- which was derived from the
idea behind "progressive disclosure in API design" and "gradual typing" as
well as borrowed some ideas from the implementation of Apple's Swift
Observation and SwiftData.

The idea behind "progressive control in macro expansion" is quite simple:
If there are no conflicts happen, then the programmer shall not pay any
efforts to workaround the conflicts resolving mechanisms. Or, there must
be tools that allow the programmer to resolve the conflicts with minimal
effort.

### Maximize the Probability of the Lucky Case

If a programmer does not have to resolve any conflicts while applying
Swift macros, then we can say the programmer gets a lucky case. To
maximize the probability that the user of a Swift macro gets a lucky case,
we must:

> Item 1: Macros that manipulate control flow should have names that
> reflect this purpose.

This item is for getting avoid misuse of the previously mentioned
`#unwrap` macro:

```swift
func foo(_ bar: Int?) {
  for _ in 0..<10 {
    #unwrap(bar) {
      print(bar)
    }
  }
}
```

which is expanded into:

```swift
func foo(_ bar: Int?) {
  for _ in 0..<10 {
    // #unwrapped expansion began
    guard let bar = bar else {
      return
    }
    print(bar)
    // #unwrapped expansion ended
  }
}
```

The programmers could be much easier to get rid of such a pitfall by
renaming this macro into `#returnIfAnyOptional`.

> Item 2: Put the macro expansion under an "umbrella" if this matches your
> design.

This would make your macro expansion get rid of most member redeclaration
errors. For example, to get avoid resolving the name conflict that is
caused by the variable shadowing in the `#unwrap` macro, we can use a
**closure** as the "umbrella" to protect the macro expansion:

Problematic expansion:

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return
  }
  // `updater` defined the second time
  let updater = Updater()
  print(bar)
  updater.update()
  // #unwrap expansion ended
  print(updater.description)
}
```

Fixed expansion with closure:

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return
  }
  { (bar) in
    // `updater` defined the second time
    let updater = Updater()
    print(bar)
    updater.update()
  }(bar)
  // #unwrap expansion ended
  print(updater.description)
}
```

However, once the body of the closure involves control flows, the closure
would not get inlined by the optimizer in its performance inlining pass.
This could leave the body of the closure out of the local analysis and the
optimization of the macro's apply site. In some cases, this also means to
larger code size. To get rid of this situation, we could use the local
function instead of closure and attribute the local function as
`@inline(__always)` to build the "umbrella".

Fixed expansion with local function:

```swift
func foo(_ bar: Int?) {
  // `updater` defined the first time
  let updater = Updater()
  // #unwrap expansion began
  guard let bar else {
    return true
  }
  @inline(__always)
  func unwrapped(bar: Int) -> Void {
    // `updater` defined the second time
    let updater = Updater()
    print(bar)
    updater.update()
  }
  unwrapped(bar)
  // #unwrap expansion ended
  print(updater.description)
}
```

This "umbrella"-like structure could also be in expansions of attached
macros -- the `@COW` macro's expansion declares a nested `Storage` type as
the storage. This nested type is just the "umbrella" -- it protects its
member from redeclaration with a type scope.

```swift
@COW
struct User {

  // @COW expansion began
  private struct Storage {

    var name: String

    // other properties ...

  }

  // Unnecessary expansions ...

  // @COW expansion ended
  
  // Unnecessary contents ...

}
```

> Item 3: Referring types, functions or variables in frameworks other than
> the standard library with fully-qualified names.

In the example of introducing the `@Box` property wrapper to the expansion
of the `@COW` macro, we can find the name `Box` itself could be ambiguous
since there might be other imported frameworks also has a property wrapper
called `Box`. We can fix this by using the fully-qualified name of the
`Box` property wrapper bundled with the library of the `@COW` macro. Let's
say the name of the library is just `COW` then the fully-qualified name of
`Box` is `COW.Box`.

The macro expansion before the fix:

```swift
@COW
struct User {

  // @COW expansion began

  // Unnecessary expansions ...
  
  @Box
  private var _$storage: Storage

  // Unnecessary expansions ...

  // @COW expansion ended


  // Unnecessary contents ...

}
```

The macro expansion after the fix:

```swift
@COW
struct User {

  // @COW expansion began

  // Unnecessary expansions ...
  
  @COW.Box
  private var _$storage: Storage

  // Unnecessary expansions ...

  // @COW expansion ended


  // Unnecessary contents ...

}
```

### Minimize the Effort of Resolving Conflicts

However, we cannot ensure the programmers always get lucky cases. There
must be cases that the programmers shall resolve the conflicts by
themselves. By applying aforementioned items, there are still potential
name and semantics conflicts lie ahead of us.

Since we cannot assume that one single macro author can predict what names
all other macro authors could pick, at the same time, invariant semantics
definitely should not be a property of Swift macro expansion because it
could decrease the flexibility of the Siwft Macro, we can only face these
conflicts and resolve them. An ideal situation would be to have a set of
confilcts resolving tools that lie on a smooth curve of the cost of use.
And there they are:

> Item 4: Use the programmer's implementation if something in your macro
> expansion is declared by the programmer.

With this item, the programmer still pays zero effort to resolve the
conflict. The mechanism described in this item adopted by some AST
transforming language features like `Equatable` and `Hashable` -- the
compiler implements these protocols on behalf of the programmer if each
member of the conformed type is `Equatable` or `Hashable`. It could also
be observed in Swift Observation when the programmer implemented the
`access` function or `withMutation` function. Since the mechanism itself
is ubiquitous, the learning curve should also be very gentle.

> Item 5: Offer a way to rename the declarations in your macro expansion
> when renaming the declarations is possible.

In the example of stacking up the `@COW` macro and the `@DictionaryLike`
macro on a single type, the macro expansions of the two macros generate
two `_$storage` variable. To add the renaming mechanism, we can naturally
come up with the idea that to add an argument to the macro:

```swift
@attached(member, names: arbitrary)
@attached(memberAttribute)
public macro COW(storageName: String) =
  #externalMacro(module: "COWMacros", type: "COWMacro")
```

But this would break the idea behind "progressive control in macro
expansion": If there are no conflicts happen, then the programmer shall
not care about resolving the conflicts -- the programmer shall always to
apply this macro with an argument this time. What might be something new
to you is this also could be done by macro overloading. This means there
could be multiple macros with the same name but have different
"signatures".

```swift
@attached(member, names: arbitrary)
@attached(memberAttribute)
public macro COW() =
  #externalMacro(module: "COWMacros", type: "COWMacro")

@attached(member, names: arbitrary)
@attached(memberAttribute)
public macro COW(storageName: String) =
  #externalMacro(module: "COWMacros", type: "COWMacro")
```

Firstly, let's recall the expansion before adding renaming mechanism to
each macro.

```swift
@COW
@DictionaryLike
struct User {

  // Other contents ...

  // Brought by @COW's expansion
  var _$storage: Storage

  // Brought by @DictionaryLike's expansion
  var _$storage: [String : Any] = [:]

}
```

Then, there is the expansion after adding renaming mechanism to each
macro.

```swift
@COW(storageName: "_$cowStorage")
@DictionaryLike(storageName: "_$dictStorage")
struct User {

  // Other contents ...

  // Brought by @COW's expansion
  var _$cowStorage: Storage

  // Brought by @DictionaryLike's expansion
  var _$dictStorage: [String : Any] = [:]

}
```

However, there could be generated declarations that couldn't be renamed,
such as the `get` and `set` accessor. Then we would come to the most
expansive tool to resolve conflicts:

> Item 6: Offer a way to stop code generation when the generated code
> involves unique language structures in a superstructure.

Swift Observation offers a good example of this item. Here is an example
of an `@Observable` macro attached class which also attached the
`@Capitalized` property wrapper on one of its property:

```swift
@propertyWrapper
struct Capitalized {
  
  var wrappedValue: String {
    didSet {
      wrappedValue = wrappedValue.capitalized
    }
  }
  
}

@Observable
class User {
  
  @Capitalized
  var name: String

  init(name: String) {
    self.name = name
  }
  
}
```

The code above does not compile due to the property wrapper requires the
`name` to be a stored property but `@Observable` transforms it into a
computed property. Here is the neccesary part of the expansion result:

```swift
@Observable
class User {

  // Unrelated expansion ...
  
  @Capitalized
  // @Observable expansion began
  @ObservationTracked
  // @Observable expansion ended
  var name: String {
    // @ObservationTracked expansion began
    init(initialValue) initializes(_name) {
      _name = initialValue
    }
    get {
      access(keyPath: \.name)
      return _name
    }
    set {
      withMutation(keyPath: \.name) {
        _name = newValue
      }
    }
    // @ObservationTracked expansion ended
  }
  
  // Unrelated contents ...
  
}
```

However, since Swift Observation also offers an attached macro called
`@ObservationIgnored` to stop code generation brought by `@Observable` on
applied members, we can make use of this macro to manually resolve the
conflicts.

Firstly, we have to backward the `name` property with an underscore and
then attach `@ObservationIgnored` on it.

```swift
@Observable
class User {
  
  @Capitalized
  @ObservationIgnored
  var _name: String

  // ...

}
```

Then, we can add a `name` property, implementing the observation mechanism
with Swift Observation:

```swift
@Observable
class User {

  // ...

  var name: String {
    init(initialValue) initializes(_name) {
      _name = initialValue
    }
    get {
      access(keyPath: \.name)
      return _name
    }
    set {
      withMutation(keyPath: \.name) {
        _name = newValue
      }
    }
  }

  // ...
  
}
```

Finally, we resolved this conflicts.

> Item 7: A template implementation should be included in the macro's
> documentation.

However, it is not enough to have the item 5 alone. The programmers still
could be confused about how to manually "expand" the macro by itself. To
address this, the macro authors should include a template implementation
of the macro in the its documentation. This provides programmers with the
guidance they need to proceed.

### Why I Didn't Recommend Using makeUniqueName(_:)

From the session at WWDC 2203, we learned that there is a way to get rid
of name colision: use `MacroExpansionContext.makeUniqueName(_:)`. However,
the name generated by this API is unreadable by human. Here is an example:

TODO: A screenshot shows `makeUniqueName` generated unreadable names

Do you know what it means? At least, I cannot make out what it means at
first glance. We can only understand this by resolving it with
`swift-demangle`:

TODO: A screenshot show the result of swift-demangle

Since this name could be used at debug-time, being human readable is
critical for it since this guarantees the efficiency of understanding the
purpose of code. This is the reason why I did't recommend using
`MacroExpansionContext.makeUniqueName(_:)`.

## Conslusion

In this post, we listed some typical traps and pitfalls that one could
step into while authoring Swift macros. On top of that, we also discussed
a tool set to resolve all of them: "progressive control in macro
expansion", which includes 2 goals and 7 items.

The goals of the tool set are:

- If there are no conflicts happen, then the programmer shall not pay
  any efforts to workaround the conflicts resolving mechanisms.
- Or, there must be tools that allow the programmer to resolve the
  conflicts with minimal effort.

The items in the tool set are:

1. Macros that manipulate control flow should have names that reflect this
  purpose.
2. Put the macro expansion under an "umbrella" if this matches your
  design.
3. Referring types, functions or variables in frameworks other than the
  standard library with fully-qualified names.
4. Use the programmer's implementation if something in your macro
  expansion is declared by the programmer.
5. Offer a way to rename the declarations in your macro expansion when
  renaming the declarations is possible.
6. Offer a way to stop code generation when the generated code involves
  unique language structures in a superstructure.
7. A template implementation should be included in the macro's
  documentation.

In addition, we also learned that the name generated by
`MacroExpansionContext.makeUniqueName(_:)` is unreadable for human beings.
This decreased the efficiency of understanding the purpose of code during
debugging.

## Resources

- A playground project that implements macros in this post:

TODO: URL

- The production level implementation of the `@COW` macro:

TODO: URL
